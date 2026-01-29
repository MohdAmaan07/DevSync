from django.db import models
from django.utils.text import slugify


class PortfolioSettings(models.Model):
    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="portfolio_settings",
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    show_github_stats = models.BooleanField(default=True)
    show_social_links = models.BooleanField(default=True)
    show_forked_repos = models.BooleanField(default=False)
    min_stars_to_show = models.IntegerField(default=0)
    show_contributions = models.BooleanField(default=True)
    show_recent_activity = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_languages = models.BooleanField(default=True)

    layout_style = models.CharField(
        max_length=20,
        choices=[
            ("grid", "Grid Layout"),
            ("list", "List Layout"),
            ("cards", "Card Layout"),
            ("minimal", "Minimal Layout"),
        ],
        default="grid",
    )
    projects_per_page = models.IntegerField(default=6)
    enable_dark_mode = models.BooleanField(default=False)

    allow_contact_form = models.BooleanField(default=True)
    contact_email = models.EmailField(blank=True, null=True)
    resume_file = models.FileField(upload_to="resumes/", blank=True, null=True)

    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    custom_domain = models.CharField(max_length=255, blank=True, null=True)
    is_published = models.BooleanField(default=True)

    google_analytics_id = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.display_name or self.user.email.split("@")[0])
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.display_name or self.user.email} - Portfolio Settings"

    class Meta:
        verbose_name = "Portfolio Settings"
        verbose_name_plural = "Portfolio Settings"
        indexes = [
            models.Index(fields=["slug"]),
        ]


class SocialLinks(models.Model):
    user = models.OneToOneField(
        "authentication.User", on_delete=models.CASCADE, related_name="social_links"
    )

    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    resume_url = models.URLField(blank=True, null=True)

    dev_to_url = models.URLField(blank=True, null=True)
    stackoverflow_url = models.URLField(blank=True, null=True)
    hashnode_url = models.URLField(blank=True, null=True)
    medium_url = models.URLField(blank=True, null=True)

    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    discord_username = models.CharField(max_length=100, blank=True, null=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.display_name or self.user.email} - Social Links"

    class Meta:
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"
        indexes = [
            models.Index(fields=["user"]),
        ]

class PortfolioSection(models.Model):
    SECTION_TYPES = [
        ("about", "About Me"),
        ("skills", "Skills & Technologies"),
        ("projects", "Projects"),
        ("experience", "Experience"),
        ("education", "Education"),
        ("blog", "Blog Posts"),
        ("testimonials", "Testimonials"),
        ("contact", "Contact"),
        ("custom", "Custom Section"),
    ]

    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="portfolio_sections",
    )
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["user", "section_type"]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.display_name or self.user.email} - {self.title}"


class Skill(models.Model):
    SKILL_CATEGORIES = [
        ("programming", "Programming Languages"),
        ("frontend", "Frontend Technologies"),
        ("backend", "Backend Technologies"),
        ("database", "Databases"),
        ("devops", "DevOps & Tools"),
        ("design", "Design Tools"),
        ("other", "Other Skills"),
    ]

    user = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="skills"
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    proficiency = models.IntegerField(default=50, help_text="Proficiency level (0-100)")
    icon_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "name"]
        ordering = ["-is_featured", "-proficiency", "name"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.user.display_name or self.user.email} - {self.name}"
