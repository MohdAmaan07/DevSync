from django.urls import path
from .views import DashboardView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', DashboardView, basename='dashboard')

urlpatterns = router.urls