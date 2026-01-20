from django.apps import AppConfig


class GithubIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'github_integration'

    def ready(self):
        import github_integration.adapter 