import uuid

from django.db import models
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Theme, ThemeConfig
from .serializers import CustomThemeSerializer, ThemeConfigSerializer, ThemeSerializer
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
