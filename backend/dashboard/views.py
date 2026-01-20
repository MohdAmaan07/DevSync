from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from authentication.permissions import IsGitHubAuthenticated
from django.contrib.auth import get_user_model
from .serializers import DashboardSerializer

# Create your views here.
class DashboardView(GenericViewSet):
    permission_classes = [IsGitHubAuthenticated]
    serializer_class = DashboardSerializer
    
    @extend_schema(
        summary="Dashboard View",
        description="Renders the dashboard page for authenticated users.",
        responses={200: DashboardSerializer},
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def get(self, request):
        user = get_user_model().objects.filter(id=request.user.id)
        response = DashboardSerializer(user, many=True)
        return Response({"message": "Dashboard data", "user_filter": response.data})
        # return render(request, 'dashboard/dashboard.html', {'user_filter': user_filter})