import requests
from allauth.socialaccount.models import SocialAccount
from django.conf import settings

from github_integration.models import GithubProfile


def revoke_github_token(user):
    """
    Revokes the GitHub access token for the given user.
    """
    github_account = SocialAccount.objects.filter(user=user, provider="github").first()

    if not github_account:
        return False

    github_token = GithubProfile.objects.filter(
        github_username=user.github_username
    ).first()

    if not github_token:
        return False

    response = requests.delete(
        f"{settings.GITHUB_BASE_URL}/applications/{settings.GITHUB_CLIENT_ID}/grant",
        auth=(settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET),
        json={"access_token": github_token.access_token},
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "YourAppName",
        },
        timeout=5,
    )

    return response.status_code == 204
