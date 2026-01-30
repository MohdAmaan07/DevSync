from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CompletePortfolioView,
    PortfolioSectionsViewSet,
    PortfolioSettingsView,
    SkillsViewSet,
    SocialLinksView,
)

router = DefaultRouter()
router.register(r"sections", PortfolioSectionsViewSet, basename="sections")
router.register(r"skills", SkillsViewSet, basename="skills")

urlpatterns = [
    path("", include(router.urls)),
    path("settings/", PortfolioSettingsView.as_view(), name="portfolio-settings"),
    path("social-links/", SocialLinksView.as_view(), name="social-links"),
    path("complete/", CompletePortfolioView.as_view(), name="complete-portfolio"),
]
