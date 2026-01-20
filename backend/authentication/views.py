from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema
from authentication.permissions import IsGitHubAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from django.contrib.auth import logout
from .utils import revoke_github_token
from .serializers import UserSerializer, UserLogoutResponseSerializer


# Create your views here.
class AuthenticationView(GenericViewSet):
    permission_classes = [IsGitHubAuthenticated]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    
    @extend_schema(
        summary="Get Authenticated User",
        description="Checks if the user is authenticated and has GitHub access.",
        responses={200: UserSerializer},
    )
    @action(detail=False, methods=["get"], url_path="user")
    def get_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Authentication Logout",
        description="Logs out the authenticated user.",
        responses={200: UserLogoutResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        if request.user.is_authenticated:
            revoke_github_token(request.user)
            
        logout(request)
        return Response(UserLogoutResponseSerializer({"message": "User has been logged out."}).data)
    

