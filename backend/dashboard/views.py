from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from github_integration.models import GithubProfile
from github_integration.tasks import sync_repositories_task

from .serializers import DashboardResponseSerializer, SyncNowResponseSerializer


# Create your views here.
@extend_schema(tags=["Dashboard"])
class DashboardView(GenericViewSet):
    def get_serializer_class(self):
        if self.action == "sync_now":
            return SyncNowResponseSerializer
        return DashboardResponseSerializer

    def get_queryset(self):
        return (
            get_user_model()
            .objects.select_related("github_profile")
            .prefetch_related("github_profile__repositories")
            .filter(pk=self.request.user.pk)
        )

    @extend_schema(
        summary="Dashboard View",
        description="Renders the dashboard page for authenticated users.",
        request=None,
        responses={200: DashboardResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def get(self, request):
        user = self.get_queryset().get()
        serializer = self.get_serializer(user)
        return Response(
            {
                "message": "Dashboard data",
                "user_filter": serializer.data,
            }
        )

    @extend_schema(
        summary="Dashboard Sync",
        description="Triggers synchronization of GitHub repositories for the authenticated user.",
        request=None,
        responses={200: SyncNowResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="sync")
    def sync_now(self, request):
        github_username = request.user.github_username
        token = (
            GithubProfile.objects.filter(github_username=github_username)
            .first()
            .access_token
        )
        if not token:
            return Response({"error": "Token not found"}, status=400)

        sync_repositories_task.enqueue(request.user.id, token)
        serializer = SyncNowResponseSerializer({"message": "Sync started"})
        return Response(serializer.data)
