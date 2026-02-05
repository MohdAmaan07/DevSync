from rest_framework.routers import DefaultRouter

from .views import GithubSyncView

router = DefaultRouter()
router.register(r"", GithubSyncView, basename="github-integration")

urlpatterns = router.urls