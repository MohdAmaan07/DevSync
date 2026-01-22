from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth import get_user_model, logout
from drf_spectacular.utils import extend_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.permissions import IsGitHubAuthenticated

from .serializers import (
    UserResponseSerializer,
    UserLogoutRequestSerializer,
    GitHubDisconnectRequestSerializer,
    GitHubDisconnectResponseSerializer,
    UserLogoutResponseSerializer,
    AuthTokenResponseSerializer,
)
from .utils import revoke_github_token, logout


# Create your views here.
@extend_schema(tags=["Auth"])
class AuthenticationView(GenericViewSet):
    permission_classes = [IsAuthenticated, IsGitHubAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    queryset = get_user_model().objects.all()

    @extend_schema(
        summary="Get Auth Token",
        description="Returns the authentication token for the user.",
        request=None,
        responses={200: AuthTokenResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="token")
    def get_token(self, request):
        refresh = RefreshToken.for_user(request.user)
        serializer = AuthTokenResponseSerializer(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
        return Response(serializer.data)

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
        request=UserLogoutRequestSerializer,
        responses={200: UserLogoutResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="logout")
    def logout_user(self, request):
        result = logout(request)

        serializer = UserLogoutResponseSerializer(result["data"])
        return Response(serializer.data, status=result["status"])

    @extend_schema(
        summary="Revoke GitHub Token",
        description="Revokes the GitHub access token for the authenticated user.",
        request=GitHubDisconnectRequestSerializer,
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

        SocialAccount.objects.filter(user=request.user, provider="github").delete()
        SocialToken.objects.filter(
            account__user=request.user, account__provider="github"
        ).delete()

        result = logout(request)
        
        if result["status"] != 200:
            return Response(
                GitHubDisconnectResponseSerializer(
                    {"message": "GitHub token revoked, but failed to logout user."}
                ).data,
                status=result["status"],
            )

        return Response(
            GitHubDisconnectResponseSerializer(
                {"message": "GitHub token revoked successfully."}
            ).data
        )
