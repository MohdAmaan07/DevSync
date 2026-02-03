import uuid

from django.db import models
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Theme, ThemeConfig
from .serializers import CustomThemeSerializer, ThemeConfigSerializer, ThemeSerializer, ThemeRequestSerializer
from .presets import THEME_PRESETS


# Create your views here.
@extend_schema(tags=["Themes"])
class ThemeView(APIView):
    serializer_class = ThemeSerializer

    def get(self, request):
        if request.user.is_authenticated:
            themes = Theme.objects.filter(
                models.Q(is_custom=False) | models.Q(created_by=request.user)
            )
        else:
            themes = Theme.objects.filter(is_custom=False)

        serializer = ThemeSerializer(themes, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Theme Configurations"])
class ThemeConfigViewSet(ModelViewSet):
    queryset = ThemeConfig.objects.all()
    serializer_class = ThemeConfigSerializer

    def get_queryset(self):
        return ThemeConfig.objects.filter(settings__user=self.request.user)

    @extend_schema(
        request=ThemeRequestSerializer,
        responses={200: ThemeConfigSerializer},
    )
    @action(detail=False, methods=["post"])
    def apply_theme(self, request):
        theme_id = request.data.get("theme_id")
        reset_overrides = request.data.get("reset_overrides", True)

        if not theme_id:
            return Response(
                {"error": "theme_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            theme = Theme.objects.get(id=theme_id)
        except Theme.DoesNotExist:
            return Response(
                {"error": "Theme not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if theme.is_custom and theme.created_by != request.user:
            return Response(
                {"error": "Cannot apply another user's custom theme"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            settings = request.user.portfolio_settings
        except Exception:
            return Response(
                {"error": "Portfolio settings not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if reset_overrides:
            defaults = {
                "theme": theme,
                # Reset all overrides when applying new theme
                "primary_color": None,
                "secondary_color": None,
                "background_color": None,
                "accent_color": None,
                "text_color": None,
                "font_family": None,
                "spacing": None,
                "border_radius": 0,
                "dark_mode_enabled": False,
            }
        
        else:
            defaults = {
                "theme": theme,
            }
            
        theme_config, created = ThemeConfig.objects.update_or_create(
            settings=settings,
            defaults=defaults
        )

        return Response(
            {
                "message": f"Theme '{theme.name}' applied successfully",
                "config": ThemeConfigSerializer(theme_config).data,
            },
            status=status.HTTP_200_OK,
        )



@extend_schema(tags=["Custom Themes"])
class CustomThemeViewSet(ModelViewSet):
    serializer_class = CustomThemeSerializer

    def get_queryset(self):
        return Theme.objects.filter(created_by=self.request.user, is_custom=True)

    def create(self, request, *args, **kwargs):
        key = request.data.get("key")
        if not key:
            return Response(
                {"error": "Theme key is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Theme.objects.filter(key=key).exists():
            return Response(
                {"error": f"Theme with key '{key}' already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_custom=True)

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        try:
            original = Theme.objects.get(pk=pk)
        except Theme.DoesNotExist:
            return Response(
                {"error": "Theme not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if original.is_custom and original.created_by != request.user:
            return Response(
                {"error": "Cannot clone another user's custom theme"},
                status=status.HTTP_403_FORBIDDEN,
            )

        unique_key = f"{original.key}-{request.user.id}-{uuid.uuid4().hex[:8]}"

        config_data = original.default_config
        if not config_data and not original.is_custom:
            config_data = THEME_PRESETS.get(original.key, {})

        custom_theme = Theme.objects.create(
            name=f"{original.name} (Copy)",
            key=unique_key,
            description=original.description,
            default_config=config_data,
            is_custom=True,
            created_by=request.user,
        )

        return Response(
            {
                "message": "Theme cloned successfully",
                "theme": CustomThemeSerializer(custom_theme).data,
            },
            status=status.HTTP_201_CREATED,
        )
