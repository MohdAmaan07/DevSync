from rest_framework import serializers

from themes.models import Theme, ThemeConfig

from .models import PortfolioSection, PortfolioSettings, Skill, SocialLinks


class PortfolioThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ("name", "key", "description")


class PortfolioThemeConfigSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(), allow_null=True, required=False
    )
    theme_details = PortfolioThemeSerializer(source="theme", read_only=True)

    class Meta:
        model = ThemeConfig
        exclude = ("id", "settings")


class PortfolioSettingSerializer(serializers.ModelSerializer):
    theme_config = PortfolioThemeConfigSerializer(allow_null=True, required=False)
    resume_url = serializers.URLField(allow_blank=True, allow_null=True, required=False)
    custom_domain = serializers.URLField(
        allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = PortfolioSettings
        exclude = ("user",)

    def update(self, instance, validated_data):
        config_data = validated_data.pop("theme_config", None)

        instance = super().update(instance, validated_data)

        if config_data is not None:
            config_obj, _ = ThemeConfig.objects.get_or_create(settings=instance)
            config_serializer = PortfolioThemeConfigSerializer(
                config_obj, data=config_data, partial=True
            )
            config_serializer.is_valid(raise_exception=True)
            config_serializer.save()

        return instance


class PortfolioSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioSection
        exclude = ("user",)


class SkillSerializer(serializers.ModelSerializer):
    icon_url = serializers.URLField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Skill
        exclude = ("user",)


class SocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLinks
        exclude = ("user",)


class PortfolioResponseSerializer(serializers.Serializer):
    settings = PortfolioSettingSerializer()
    sections = PortfolioSectionSerializer(many=True)
    social_links = SocialLinksSerializer()
    skills = SkillSerializer(many=True)
    theme_config = PortfolioThemeConfigSerializer(allow_null=True, required=False)
