from allauth.socialaccount.models import SocialAccount
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.permissions import IsGitHubAuthenticated

from .models import PortfolioSection, PortfolioSettings, Skill, SocialLinks
from .serializers import (
    PortfolioResponseSerializer,
    PortfolioSectionSerializer,
    PortfolioSettingSerializer,
    SkillSerializer,
    SocialLinksSerializer,
)


# Create your views here.
@extend_schema(tags=["Portfolio"])
class PortfolioViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated, IsGitHubAuthenticated]

    def get_queryset(self):
        if self.action == "get_portfolio_settings":
            return PortfolioSettings.objects.filter(user=self.request.user)
        elif self.action == "set_portfolio_settings":
            return PortfolioSettings.objects.filter(user=self.request.user)
        elif self.action == "get_portfolio_sections":
            return PortfolioSection.objects.filter(user=self.request.user)
        elif self.action == "set_portfolio_sections":
            return PortfolioSection.objects.filter(user=self.request.user)
        elif self.action == "get_social_links":
            return SocialLinks.objects.filter(user=self.request.user)
        elif self.action == "set_social_links":
            return SocialLinks.objects.filter(user=self.request.user)
        return PortfolioSettings.objects.none()

    @extend_schema(
        summary="Get Portfolio Settings",
        description="Retrieve the portfolio settings for the authenticated user.",
        request=None,
        responses={200: PortfolioSettingSerializer},
    )
    @action(detail=False, methods=["get"], url_path="settings")
    def get_portfolio_settings(self, request):
        portfolio_settings = self.get_queryset().first()
        serializer = PortfolioSettingSerializer(portfolio_settings)
        return Response(serializer.data)

    @extend_schema(
        summary="Set Portfolio Settings",
        description="Update the portfolio settings for the authenticated user.",
        request=PortfolioSettingSerializer,
        responses={200: PortfolioSettingSerializer},
    )
    @action(detail=False, methods=["post"], url_path="settings")
    def set_portfolio_settings(self, request):
        portfolio_settings = self.get_queryset().first()
        serializer = PortfolioSettingSerializer(
            portfolio_settings, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Get Portfolio Sections",
        description="Retrieve the portfolio sections for the authenticated user.",
        request=None,
        responses={200: PortfolioSectionSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="sections")
    def get_portfolio_sections(self, request):
        sections = PortfolioSection.objects.filter(user=request.user).order_by("order")
        serializer = PortfolioSectionSerializer(sections, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Set Portfolio Sections",
        description="Update the portfolio sections for the authenticated user.",
        request=PortfolioSectionSerializer(many=True),
        responses={200: PortfolioSectionSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="sections")
    def set_portfolio_sections(self, request):
        sections = PortfolioSection.objects.filter(user=request.user)
        serializer = PortfolioSectionSerializer(
            sections, data=request.data, many=True, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Get Social Links",
        description="Retrieve the social links for the authenticated user.",
        request=None,
        responses={200: SocialLinksSerializer},
    )
    @action(detail=False, methods=["get"], url_path="social-links")
    def get_social_links(self, request):
        social_links = SocialLinks.objects.filter(user=request.user).first()
        serializer = SocialLinksSerializer(social_links)
        return Response(serializer.data)

    @extend_schema(
        summary="Set Social Links",
        description="Update the social links for the authenticated user.",
        request=SocialLinksSerializer,
        responses={200: SocialLinksSerializer},
    )
    @action(detail=False, methods=["post"], url_path="social-links")
    def set_social_links(self, request):
        social_links = SocialLinks.objects.filter(user=request.user).first()
        serializer = SocialLinksSerializer(
            social_links, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Get Skills",
        description="Retrieve the skills for the authenticated user.",
        request=None,
        responses={200: SkillSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="skills")
    def get_skills(self, request):
        skills = Skill.objects.filter(user=request.user).order_by(
            "-proficiency", "name"
        )
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Set Skills",
        description="Update the skills for the authenticated user.",
        request=SkillSerializer(many=True),
        responses={200: SkillSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="skills")
    def set_skills(self, request):
        skills = Skill.objects.filter(user=request.user)
        serializer = SkillSerializer(skills, data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Get Portfolio Sections",
        description="Retrieve the portfolio sections for the authenticated user.",
        request=None,
        responses={200: PortfolioResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="full")
    def get_full_portfolio(self, request):
        portfolio_settings = PortfolioSettings.objects.filter(user=request.user).first()
        sections = PortfolioSection.objects.filter(user=request.user).order_by("order")
        social_links = SocialLinks.objects.filter(user=request.user).first()
        skills = Skill.objects.filter(user=request.user).order_by(
            "-proficiency", "name"
        )

        response_data = {
            "settings": PortfolioSettingSerializer(portfolio_settings).data,
            "sections": PortfolioSectionSerializer(sections, many=True).data,
            "social_links": SocialLinksSerializer(social_links).data,
            "skills": SkillSerializer(skills, many=True).data,
        }

        serializer = PortfolioResponseSerializer(response_data)
        return Response(serializer.data)
