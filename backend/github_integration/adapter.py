from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialToken
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime

from .models import GithubProfile
from .tasks import sync_repositories_task

User = get_user_model()


class GitHubSocialAccountAdapter(DefaultSocialAccountAdapter):
    def _sync_github_profile(self, user, sociallogin):
        if sociallogin.account.provider == "github":
            github_username = sociallogin.account.extra_data.get("login")
            if github_username and user.github_username != github_username:
                user.github_username = github_username
                user.save(update_fields=["github_username"])

            token = None
            try:
                token = sociallogin.token.token
            except AttributeError:
                try:
                    token = SocialToken.objects.get(account=sociallogin.account).token
                except SocialToken.DoesNotExist:
                    token = None

            github_data = sociallogin.account.extra_data
            profile = {
                "github_username": github_data.get("login"),
                "github_id": github_data.get("id"),
                "access_token": token,
                "avatar_url": github_data.get("avatar_url"),
                "profile_url": github_data.get("html_url"),
                "public_repos": github_data.get("public_repos", 0),
                "followers": github_data.get("followers", 0),
                "following": github_data.get("following", 0),
                "name": github_data.get("name"),
                "bio": github_data.get("bio"),
                "company": github_data.get("company"),
                "location": github_data.get("location"),
                "blog": github_data.get("blog"),
            }

            created_at = github_data.get("created_at")
            if created_at:
                profile["joined_date"] = parse_datetime(created_at)

            GithubProfile.objects.update_or_create(user=user, defaults=profile)

            if token:
                sync_to_async(sync_repositories_task.aenqueue)(user.id, token)
        return user

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")

        if not email:
            return

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        if sociallogin.is_existing:
            return

        sociallogin.connect(request, user)
        self._sync_github_profile(sociallogin.user, sociallogin)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        self._sync_github_profile(user, sociallogin)
        return user
