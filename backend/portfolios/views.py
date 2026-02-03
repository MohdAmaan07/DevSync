from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.views import SingletonUserView
from themes.models import ThemeConfig

from .models import PortfolioSection, PortfolioSettings, Skill, SocialLinks
from .serializers import (
    PortfolioResponseSerializer,
    PortfolioSectionSerializer,
    PortfolioSettingSerializer,
    SkillSerializer,
    SocialLinksSerializer,
)


@extend_schema(tags=["Portfolio Settings"])
class PortfolioSettingsView(SingletonUserView):
    queryset = PortfolioSettings.objects.all()
    serializer_class = PortfolioSettingSerializer


@extend_schema(tags=["Social Links"])
class SocialLinksView(SingletonUserView):
    queryset = SocialLinks.objects.all()
    serializer_class = SocialLinksSerializer


@extend_schema(tags=["Portfolio Sections"])
class PortfolioSectionsViewSet(ModelViewSet):
    queryset = PortfolioSection.objects.all()
    serializer_class = PortfolioSectionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Skills"])
class SkillsViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Complete Portfolio"])
class CompletePortfolioView(APIView):
    serializer_class = PortfolioResponseSerializer

    def get(self, request):
        user = request.user
        data = {
            "settings": PortfolioSettings.objects.filter(user=user).first(),
            "sections": PortfolioSection.objects.filter(user=user).order_by("order"),
            "social_links": SocialLinks.objects.filter(user=user).first(),
            "skills": Skill.objects.filter(user=user).order_by("order"),
            "theme_config": ThemeConfig.objects.filter(settings__user=user).first(),
        }
        serializer = PortfolioResponseSerializer(data)
        return Response(serializer.data)
