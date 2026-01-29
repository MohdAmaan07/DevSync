from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class Theme(models.Model):
    name = models.CharField(max_length=100, unique=True)
    key = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["key"]),
        ]


class ThemeConfig(models.Model):
    SIZE_CHOICES = [("sm", "Small"), ("md", "Medium"), ("lg", "Large")]

    settings = models.OneToOneField(
        "portfolios.PortfolioSettings",
        on_delete=models.CASCADE,
        related_name="theme_config",
    )
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True)

    primary_color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    secondary_color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    background_color = models.CharField(
        max_length=7, blank=True, null=True
    )  # Hex color
    accent_color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    text_color = models.CharField(max_length=7, blank=True, null=True)  # Hex color

    font_family = models.CharField(max_length=100, blank=True, null=True)
    spacing = models.CharField(
        max_length=10, choices=SIZE_CHOICES, blank=True, null=True
    )  # e.g., '16px', '1em'
    spacing = models.CharField(max_length=20, blank=True, null=True)  #

    dark_mode_enabled = models.BooleanField(default=False)
    border_radius = models.PositiveBigIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # in pixels

    updated_at = models.DateTimeField(auto_now=True)
