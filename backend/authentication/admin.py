from django.contrib import admin

from .models import User


# Register your models here.
class ModelAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "github_username",
        "portfolio_slug",
        "is_portfolio_public",
    )
    search_fields = ("username", "email", "github_username")
    list_filter = ("github_username", "username")


admin.site.register(User, ModelAdmin)
