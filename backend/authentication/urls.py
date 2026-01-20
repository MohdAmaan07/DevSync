from django.urls import path
from .views import AuthenticationView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', AuthenticationView, basename='authentication')

urlpatterns = router.urls