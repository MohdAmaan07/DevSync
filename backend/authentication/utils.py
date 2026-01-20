import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.conf import settings

def revoke_github_token(user):
    """
    Revokes the GitHub access token for the given user.
    """
    github_account = SocialAccount.objects.filter(user=user, provider="github").first()
    github_token = SocialToken.objects.filter(account=github_account).first()
    
    if not github_account or not github_token:
        return False
    
    response = requests.delete(
        f"https://api.github.com/applications/{settings.GITHUB_CLIENT_ID}/token",
        auth=(settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET),
        json={"access_token": github_token.token},
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "YourAppName",
        },
        timeout=5,
    )
    
    response.status_code == 204