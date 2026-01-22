from rest_framework.routers import DefaultRouter

from .views import DashboardView

router = DefaultRouter()
router.register(r"", DashboardView, basename="dashboard")

urlpatterns = router.urls
