from rest_framework.serializers import ModelSerializer, Serializer

from themes.models import Theme, ThemeConfig

from .models import PortfolioSection, PortfolioSettings, Skill, SocialLinks


class ThemeSerializer(ModelSerializer):
    class Meta:
        model = Theme
        exclude = ("id",)


class ThemeConfigSerializer(ModelSerializer):
    class Meta:
        model = ThemeConfig
        exclude = ("id",)


class PortfolioSettingSerializer(ModelSerializer):
    class Meta:
        model = PortfolioSettings
        exclude = ("id", "user")

    theme = ThemeSerializer(allow_null=True)
    theme_config = ThemeConfigSerializer(allow_null=True)


class PortfolioSectionSerializer(ModelSerializer):
    class Meta:
        model = PortfolioSection
        exclude = ("id", "user")


class SocialLinksSerializer(ModelSerializer):
    class Meta:
        exclude = ("id", "user")
        model = SocialLinks


class SkillSerializer(ModelSerializer):
    class Meta:
        model = Skill
        exclude = ("id", "user")


class PortfolioResponseSerializer(Serializer):
    settings = PortfolioSettingSerializer()
    sections = PortfolioSectionSerializer(many=True)
    social_links = SocialLinksSerializer(allow_null=True)
    skills = SkillSerializer(many=True)
