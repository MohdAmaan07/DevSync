from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema

from .serializers import SyncNowResponseSerializer
from .models import GithubProfile
from .tasks import (
    sync_repositories_task,
    sync_commits_task,
    sync_all_task,
)


# Create your views here.
@extend_schema(tags=["GitHub Integration"])
class GithubSyncView(GenericViewSet):
    @extend_schema(
        summary="Sync Repositories Now",
        description="Triggers synchronization of GitHub repositories for the authenticated user.",
        request=None,
        responses={200: SyncNowResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="sync-repo")
    def sync_repo(self, request):
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

    @extend_schema(
        summary="Sync Commits Now",
        description="Triggers synchronization of GitHub commits for the authenticated user.",
        request=None,
        responses={200: SyncNowResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="sync-commits")
    def sync_commits(self, request):
        github_username = request.user.github_username
        token = (
            GithubProfile.objects.filter(github_username=github_username)
            .first()
            .access_token
        )
        if not token:
            return Response({"error": "Token not found"}, status=400)

        sync_commits_task.enqueue(request.user.id, token)
        serializer = SyncNowResponseSerializer({"message": "Commit sync started"})
        return Response(serializer.data)

    @extend_schema(
        summary="Sync All GitHub Data Now",
        description="Triggers synchronization of all GitHub data for the authenticated user.",
        request=None,
        responses={200: SyncNowResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="sync-all")
    def sync_all(self, request):
        github_username = request.user.github_username
        token = (
            GithubProfile.objects.filter(github_username=github_username)
            .first()
            .access_token
        )
        if not token:
            return Response({"error": "Token not found"}, status=400)

        sync_all_task.enqueue(request.user.id, token)
        serializer = SyncNowResponseSerializer({"message": "Full sync started"})
        return Response(serializer.data)
