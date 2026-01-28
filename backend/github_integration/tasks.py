from django.tasks import task

from .sync import sync_repositories


@task
def sync_repositories_task(github_id, token):
    sync_repositories(github_id, token)
