from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import DashboardResponseSerializer


# Create your views here.
@extend_schema(tags=["Dashboard"])
class DashboardView(GenericViewSet):
    def get_queryset(self):
        return (
            get_user_model().
            objects.select_related("github_profile")
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
