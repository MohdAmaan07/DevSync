from django.contrib import admin
from .models import PortfolioSettings, PortfolioSection, SocialLinks, Skill

# Register your models here.
class PortfolioSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "custom_domain", "is_published", "created_at", "updated_at")
    search_fields = ("user__email", "custom_domain")
    list_filter = ("is_published", "created_at", "updated_at")

class SocialLinksAdmin(admin.ModelAdmin):
    list_display = ("user", "linkedin_url", "github_url", "website_url", "created_at", "updated_at")
    search_fields = ("user__email", "linkedin_url", "github_url", "website_url")
    list_filter = ("created_at", "updated_at")
    
class PortfolioSectionAdmin(admin.ModelAdmin):
    list_display = ("user", "section_type", "order", "created_at", "updated_at")
    search_fields = ("user__email", "section_type")
    list_filter = ("section_type", "created_at", "updated_at")
    
class SkillAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "proficiency", "created_at")
    search_fields = ("user__email", "name")
    list_filter = ("proficiency", "created_at")
    
admin.site.register(PortfolioSettings, PortfolioSettingsAdmin)
admin.site.register(SocialLinks, SocialLinksAdmin)
admin.site.register(PortfolioSection, PortfolioSectionAdmin)
admin.site.register(Skill, SkillAdmin)