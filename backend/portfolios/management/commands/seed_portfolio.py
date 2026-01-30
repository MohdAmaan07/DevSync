import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from portfolios.models import PortfolioSection, PortfolioSettings, Skill, SocialLinks
from themes.models import Theme, ThemeConfig

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed database with dummy portfolio data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Create Themes
        themes = []
        for name in ["Midnight", "Ocean", "Emerald", "Sunset"]:
            theme, _ = Theme.objects.get_or_create(
                name=name,
                key=name.lower(),
                description=f"A beautiful {name} inspired theme.",
            )
            themes.append(theme)

        # 2. Get or Create Users
        users = User.objects.all()[:5]
        if not users:
            self.stdout.write("No users found. Please create some users first.")
            return

        for user in users:
            self.stdout.write(f"Seeding for user: {user.email}")

            # 3. Portfolio Settings
            settings, _ = PortfolioSettings.objects.get_or_create(
                user=user,
                defaults={
                    "show_github_stats": True,
                    "layout_style": random.choice(["grid", "list", "cards"]),
                    "enable_dark_mode": random.choice([True, False]),
                    "meta_title": f"{user.get_username()}'s Portfolio",
                },
            )

            # 4. Social Links
            SocialLinks.objects.get_or_create(
                user=user,
                defaults={
                    "github_url": f"https://github.com/{user.get_username() or 'user'}",
                    "linkedin_url": "https://linkedin.com/in/dummy",
                    "twitter_url": "https://twitter.com/dummy",
                },
            )

            # 5. Portfolio Sections
            section_types = ["about", "skills", "projects", "experience"]
            for i, s_type in enumerate(section_types):
                PortfolioSection.objects.get_or_create(
                    user=user,
                    section_type=s_type,
                    defaults={
                        "title": s_type.capitalize(),
                        "content": fake.paragraph(nb_sentences=3),
                        "order": i,
                        "is_enabled": True,
                    },
                )

            # 6. Skills
            skill_list = [
                ("Python", "backend"),
                ("Django", "backend"),
                ("React", "frontend"),
                ("PostgreSQL", "database"),
                ("Docker", "devops"),
                ("Figma", "design"),
            ]
            for name, cat in skill_list:
                Skill.objects.get_or_create(
                    user=user,
                    name=name,
                    defaults={
                        "category": cat,
                        "proficiency": random.randint(60, 100),
                        "is_featured": random.choice([True, False]),
                    },
                )

            # 7. Theme Config
            ThemeConfig.objects.get_or_create(
                settings=settings,
                defaults={
                    "theme": random.choice(themes),
                    "primary_color": fake.hex_color(),
                    "secondary_color": fake.hex_color(),
                    "border_radius": random.randint(0, 20),
                    "dark_mode_enabled": settings.enable_dark_mode,
                },
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded portfolio data!"))
