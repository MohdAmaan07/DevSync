from urllib.parse import urlencode

import requests
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialToken
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.dateparse import parse_datetime
from rest_framework_simplejwt.tokens import RefreshToken

from .models import GithubProfile, Repository


class GitHubSocialAccountAdapter(DefaultSocialAccountAdapter):
    def login(self, request, sociallogin):
        super().login(request, sociallogin)
        
        user = sociallogin.user
        refresh = RefreshToken.for_user(user)
        params = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return JsonResponse(params)
        
        
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

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

            # if token:
            #     print("Syncing repositories for user:", profile["github_username"])
            #     self.sync_repositories(user.github_profile, token)
        return user

    def sync_repositories(self, github_profile, token):
        print("Starting repository sync for:", github_profile.github_username)
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"https://api.github.com/users/repos/?per_page=100"

        while url:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                break

            repos_data = response.json()
            print(f"Fetched {len(repos_data)} repositories for user:", github_profile.github_username)
            for repo_data in repos_data:
                repo = {
                    "name": repo_data.get("name"),
                    "full_name": repo_data.get("full_name"),
                    "description": repo_data.get("description"),
                    "github_id": repo_data.get("id"),
                    "html_url": repo_data.get("html_url"),
                    "clone_url": repo_data.get("clone_url"),
                    "git_url": repo_data.get("git_url"),
                    "stars_count": repo_data.get("stargazers_count", 0),
                    "forks_count": repo_data.get("forks_count", 0),
                    "watchers_count": repo_data.get("watchers_count", 0),
                    "open_issues_count": repo_data.get("open_issues_count", 0),
                    "language": repo_data.get("language"),
                    "is_private": repo_data.get("private", False),
                    "is_fork": repo_data.get("fork", False),
                    "is_archived": repo_data.get("archived", False),
                }

                if repo.get("created_at"):
                    repo["created_at"] = parse_datetime(repo_data.get("created_at"))

                if repo.get("updated_at"):
                    repo["updated_at"] = parse_datetime(repo_data.get("updated_at"))

                if repo.get("pushed_at"):
                    repo["pushed_at"] = parse_datetime(repo_data.get("pushed_at"))

                Repository.objects.update_or_create(
                    github_profile=github_profile,
                    name=repo_data.get("name"),
                    defaults=repo,
                )

                link = response.links.get("next")
                url = link["url"] if link else None
