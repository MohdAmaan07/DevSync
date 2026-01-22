from rest_framework.routers import DefaultRouter

from .views import AuthenticationView

router = DefaultRouter()
router.register(r"", AuthenticationView, basename="authentication")

urlpatterns = router.urls
