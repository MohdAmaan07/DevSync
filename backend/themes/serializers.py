from rest_framework import serializers
from .models import Theme, ThemeConfig
from .presets import THEME_PRESETS


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ThemeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeConfig
        fields = "__all__"

    def to_representation(self, instance):
        """
        Merge user overrides with theme presets.
        """
        data = super().to_representation(instance)

        if instance.theme and instance.theme.is_custom:
            return data

        theme_key = instance.theme.key
        preset = THEME_PRESETS.get(theme_key, {})

        overridable_fields = [
            "primary_color",
            "secondary_color",
            "background_color",
            "accent_color",
            "text_color",
            "font_family",
            "spacing",
            "border_radius",
            "dark_mode_enabled",
        ]

        for field in overridable_fields:
            if data.get(field) is None or data.get(field) == "":
                if field in preset:
                    data[field] = preset[field]

        return data


class CustomThemeConfigSerializer(serializers.Serializer):
    primary_color = serializers.CharField(max_length=50, required=True)
    secondary_color = serializers.CharField(max_length=50, required=True)
    background_color = serializers.CharField(max_length=50, required=True)
    accent_color = serializers.CharField(max_length=50, required=True)
    text_color = serializers.CharField(max_length=50, required=True)
    font_family = serializers.CharField(max_length=100, required=True)
    spacing = serializers.ChoiceField(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")], required=True
    )
    dark_mode_enabled = serializers.BooleanField(required=True)
    border_radius = serializers.IntegerField(min_value=0, max_value=100, required=True)


class CustomThemeSerializer(serializers.ModelSerializer):
    config = CustomThemeConfigSerializer(required=True, write_only=True)

    class Meta:
        model = Theme
        fields = ("id", "name", "key", "description", "config", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        config_data = validated_data.pop("config", None)
        validated_data["default_config"] = config_data
        return Theme.objects.create(**validated_data)

    def update(self, instance, validated_data):
        config_data = validated_data.pop("config", None)
        if config_data:
            instance.default_config = config_data
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Include the theme's default config when retrieving."""
        data = super().to_representation(instance)
        if instance.default_config:
            data["config"] = instance.default_config
        return data