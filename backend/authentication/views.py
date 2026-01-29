from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model, logout
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.permissions import IsGitHubAuthenticated
from github_integration.models import GithubProfile

from .serializers import (
    GitHubDisconnectResponseSerializer,
    UserLogoutResponseSerializer,
    UserResponseSerializer,
)
from .utils import revoke_github_token


# Create your views here.
@extend_schema(tags=["Auth"])
class AuthenticationView(GenericViewSet):
    permission_classes = [IsAuthenticated, IsGitHubAuthenticated]
    queryset = get_user_model().objects.all()

    @extend_schema(
        summary="Get Authenticated User",
        description="Checks if the user is authenticated and has GitHub access.",
        request=None,
        responses={200: UserResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="user")
    def get_user(self, request):
        serializer = UserResponseSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Authentication Logout",
        description="Logs out the authenticated user.",
        request=None,
        responses={200: UserLogoutResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="logout")
    def logout_user(self, request):
        logout(request)
        serializer = UserLogoutResponseSerializer(
            {"message": "User has been logged out."}
        )
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="Disconnect GitHub",
        description="Revokes GitHub access token and disconnects GitHub from the user's account.",
        request=None,
        responses={
            200: GitHubDisconnectResponseSerializer,
            400: GitHubDisconnectResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="disconnect-github")
    def disconnect_github(self, request):
        success = revoke_github_token(request.user)

        if not success:
            return Response(
                GitHubDisconnectResponseSerializer(
                    {"message": "Failed to revoke GitHub token."}
                ).data,
                status=400,
            )

        GithubProfile.objects.filter(user=request.user).delete()
        request.user.github_username = None
        request.user.save(update_fields=["github_username"])

        SocialAccount.objects.filter(user=request.user, provider="github").delete()

        logout(request)

        serializer = UserLogoutResponseSerializer(
            {"message": "User has been logged out."}
        )
        return Response(serializer.data, status=200)
