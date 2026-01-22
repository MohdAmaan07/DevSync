import requests
from allauth.socialaccount.models import SocialAccount
from github_integration.models import GithubProfile
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

def revoke_github_token(user):
    """
    Revokes the GitHub access token for the given user.
    """
    github_account = SocialAccount.objects.filter(user=user, provider="github").first()

    if not github_account:
        return False

    github_token = GithubProfile.objects.filter(github_username=user.github_username).first()

    if not github_token:
        return False

    response = requests.delete(
        f"https://api.github.com/applications/{settings.GITHUB_CLIENT_ID}/token",
        auth=(settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET),
        json={"access_token": github_token.access_token},
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "YourAppName",
        },
        timeout=5,
    )

    return response.status_code == 204


def logout(request):
    """
    Logs out the user by blacklisting the refresh token.
    """
    refresh_token = request.data.get("refresh", None)

    if not refresh_token:
        return {
            "status": 400,
            "data": {"message": "Refresh token is required for logout."},
        }

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return {
            "status": 400,
            "data": {"message": "Invalid refresh token."},
        }

    return {
        "status": 200,
        "data": {"message": "User has been logged out."},
    }