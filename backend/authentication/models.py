from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    portfolio_slug = models.SlugField(unique=True, blank=True)
    github_username = models.CharField(max_length=255, blank=True, null=True)
    theme_preference = models.CharField(max_length=50, default='default')
    dark_mode = models.BooleanField(default=False)  
    is_portfolio_public = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.portfolio_slug:
            self.portfolio_slug = self.username.lower().replace(' ', '-')
        super().save(*args, **kwargs)