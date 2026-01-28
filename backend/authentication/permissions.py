import logging

import requests
from allauth.socialaccount.models import SocialAccount
from django.core.cache import cache
from rest_framework import permissions

from github_integration.models import GithubProfile

logger = logging.getLogger(__name__)


class IsGitHubAuthenticated(permissions.BasePermission):
    """
    Custom permission to check if the user is authenticated via GitHub
    and has a valid access token.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        github_account = SocialAccount.objects.filter(
            user=user, provider="github"
        ).first()
        if not github_account:
            return False

        token_obj = GithubProfile.objects.filter(
            github_username=getattr(user, "github_username", None)
        ).first()

        if not token_obj or not token_obj.access_token:
            return False

        cache_key = f"github_token_valid_{user.id}"
        is_valid = cache.get(cache_key)

        if is_valid is not None:
            return is_valid

        try:
            headers = {
                "Authorization": f"token {token_obj.access_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            response = requests.get(
                "https://api.github.com/user", headers=headers, timeout=5
            )

            if response.status_code == 200:
                cache.set(cache_key, True, 600)
                return True
            else:
                cache.set(cache_key, False, 60)
                return False

        except requests.RequestException as e:
            logger.error(f"GitHub API connection error: {e}")
            return False
