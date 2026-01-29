from django.contrib import admin

from .models import Commit, GithubProfile, GitHubSyncLog, Repository


# Register your models here.
class ModelGithubProfileAdmin(admin.ModelAdmin):
    list_display = (
        "github_username",
        "user",
        "auto_sync",
        "sync_frequency",
        "last_sync",
    )
    search_fields = ("github_username", "user__email")
    list_filter = ("auto_sync", "sync_frequency")


class ModelRepositoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "github_profile",
        "description",
        "html_url",
        "is_fork",
        "created_at_github",
    )
    search_fields = ("name", "github_profile__github_username")
    list_filter = ("is_fork", "created_at_github")


class ModelCommitAdmin(admin.ModelAdmin):
    list_display = (
        "repository",
        "sha",
        "github_profile__github_username",
        "message",
        "date",
    )
    search_fields = ("sha", "github_profile__github_username", "repository__name")
    list_filter = ("date",)


class ModelGitHubSyncLogAdmin(admin.ModelAdmin):
    list_display = ("github_profile", "status", "completed_at", "status")
    search_fields = ("github_profile__github_username", "status")
    list_filter = ("status", "completed_at")


admin.site.register(GithubProfile, ModelGithubProfileAdmin)
admin.site.register(Repository, ModelRepositoryAdmin)
admin.site.register(Commit, ModelCommitAdmin)
admin.site.register(GitHubSyncLog, ModelGitHubSyncLogAdmin)
