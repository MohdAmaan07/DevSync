import requests
from rest_framework import permissions
from allauth.socialaccount.models import SocialAccount, SocialToken

class IsGitHubAuthenticated(permissions.BasePermission):
    """
    Custom permission to check if the user is authenticated via GitHub
    and has a valid access token.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        github_account = SocialAccount.objects.filter(user=user, provider="github").first()
        if not github_account:
            return False

        token_obj = SocialToken.objects.filter(account=github_account).first()
        if not token_obj or not getattr(token_obj, "token", None):
            return False

        headers = {
            "Authorization": f"token {token_obj.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        response = requests.get("https://api.github.com/user", headers=headers)

        if response.status_code != 200:
            return False

        return True