from django.core.management.base import BaseCommand

from themes.models import Theme

THEMES = [
    {
        "key": "minimal",
        "name": "Minimal",
        "description": "Clean, whitespace-heavy layout.",
    },
    {
        "key": "modern",
        "name": "Modern",
        "description": "Modern responsive card-based layout.",
    },
    {
        "key": "classic",
        "name": "Classic",
        "description": "Resume-like structured portfolio layout.",
    },
    {
        "key": "terminal",
        "name": "Terminal",
        "description": "Monospace CLI/terminal vibe.",
    },
    {"key": "glass", "name": "Glass", "description": "Glassmorphism + blur aesthetic."},
    {
        "key": "professional",
        "name": "Professional",
        "description": "Corporate clean theme for recruiters.",
    },
    {
        "key": "creative",
        "name": "Creative",
        "description": "Bold accents + visual design.",
    },
]


class Command(BaseCommand):
    help = "Seed the database with default themes."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for theme in THEMES:
            Theme.objects.update_or_create(
                key=theme["key"],
                defaults={
                    "name": theme["name"],
                    "description": theme["description"],
                },
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(THEMES)} themes, created {created_count}, updated {updated_count}."
            )
        )
