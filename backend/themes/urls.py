from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomThemeViewSet, ThemeConfigViewSet, ThemeView

router = DefaultRouter()
router.register(r"theme-configs", ThemeConfigViewSet, basename="themeconfig")
router.register(r"custom-themes", CustomThemeViewSet, basename="customtheme")

urlpatterns = [
    path("", ThemeView.as_view(), name="theme-list"),
    path("", include(router.urls)),
]
