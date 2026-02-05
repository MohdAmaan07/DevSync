from django.contrib import admin

from .models import Theme, ThemeConfig


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "is_custom", "created_by", "created_at"]
    list_filter = ["is_custom", "created_at"]
    search_fields = ["name", "key", "created_by__username"]
    readonly_fields = ["created_at"]


@admin.register(ThemeConfig)
class ThemeConfigAdmin(admin.ModelAdmin):
    list_display = ["settings", "theme", "updated_at"]
    list_filter = ["theme", "dark_mode_enabled"]
    search_fields = ["settings__user__username"]
    readonly_fields = ["updated_at"]
