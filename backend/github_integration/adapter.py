from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class GitHubSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if sociallogin.account.provider == "github":
            github_username = sociallogin.account.extra_data.get("login")
            if github_username and user.github_username != github_username:
                user.github_username = github_username
                user.save(update_fields=["github_username"])

        return user