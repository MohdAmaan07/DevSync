from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import (
    DashboardRequestSerializer,
    DashboardResponseSerializer,
)


# Create your views here.
@extend_schema(tags=["Dashboard"])
class DashboardView(GenericViewSet):
    serializer_class = DashboardResponseSerializer

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
        parameters=[DashboardRequestSerializer],
        responses={200: DashboardResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        serializer = DashboardRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        repo_count = serializer.validated_data.get("repository_count")
        user = self.get_queryset().get()
        serializer = self.get_serializer(user, context={"repository_count": repo_count})
        return Response(serializer.data)
