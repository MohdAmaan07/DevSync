from django.db import models
from encrypted_fields.fields import EncryptedCharField


# Create your models here.
class GithubProfile(models.Model):
    SYNC_FREQUENCY_CHOICES = [
        ("hourly", "Hourly"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("manual", "Manual Only"),
    ]

    user = models.OneToOneField(
        "authentication.User", on_delete=models.CASCADE, related_name="github_profile"
    )
    github_username = models.CharField(max_length=255, unique=True)
    github_id = models.BigIntegerField(unique=True)
    access_token = EncryptedCharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    profile_url = models.URLField(blank=True, null=True)

    # GitHub Stats
    public_repos = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    joined_date = models.DateTimeField(null=True, blank=True)

    # Profile Data
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    blog = models.URLField(blank=True, null=True)

    # Sync Settings
    auto_sync = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(
        max_length=20, choices=SYNC_FREQUENCY_CHOICES, default="daily"
    )

    # Repository Filtering
    show_forked_repos = models.BooleanField(default=False)
    excluded_repos = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.github_username} ({self.user.email})"

    class Meta:
        verbose_name = "GitHub Profile"
        verbose_name_plural = "GitHub Profiles"
        indexes = [
            models.Index(fields=["github_username"]),
        ]


class Repository(models.Model):
    github_profile = models.ForeignKey(
        GithubProfile, on_delete=models.CASCADE, related_name="repositories"
    )

    # Basic Info
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    github_id = models.BigIntegerField(unique=True)

    # URLs
    html_url = models.URLField()
    clone_url = models.URLField()
    git_url = models.URLField()

    # Stats
    stars_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    watchers_count = models.IntegerField(default=0)
    open_issues_count = models.IntegerField(default=0)

    # Repository Properties
    language = models.CharField(max_length=100, blank=True, null=True)
    languages = models.JSONField(default=dict, blank=True)
    topics = models.JSONField(default=list, blank=True)

    # Flags
    is_private = models.BooleanField(default=False)
    is_fork = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    # Dates
    created_at_github = models.DateTimeField(null=True, blank=True)
    updated_at_github = models.DateTimeField(null=True, blank=True)
    pushed_at_github = models.DateTimeField(null=True, blank=True)

    # Portfolio Display Settings
    is_featured = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    custom_description = models.TextField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)

    # Sync Info
    last_synced = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["-is_featured", "-stars_count", "-updated_at_github"]
        unique_together = ["github_profile", "name"]
        indexes = [
            models.Index(fields=["github_id"]),
            models.Index(fields=["github_profile", "is_hidden"]),
        ]


class Commit(models.Model):
    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="commits"
    )
    github_profile = models.ForeignKey(
        GithubProfile, on_delete=models.CASCADE, related_name="commits"
    )

    sha = models.CharField(max_length=40, unique=True)
    message = models.TextField()
    date = models.DateTimeField()

    # Stats for contribution graph
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    total_changes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.repository.name} - {self.sha[:7]}"

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["sha"]),
            models.Index(fields=["repository", "date"]),
        ]


class GitHubSyncLog(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
        ("partial", "Partial Success"),
    ]

    github_profile = models.ForeignKey(
        GithubProfile, on_delete=models.CASCADE, related_name="sync_logs"
    )
    sync_type = models.CharField(max_length=50)  # 'profile', 'repositories', 'commits'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # Sync Results
    repos_synced = models.IntegerField(default=0)
    commits_synced = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.github_profile.github_username} - {self.sync_type} - {self.status}"
        )

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["github_profile", "sync_type", "status"]),
        ]
