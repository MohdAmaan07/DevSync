from django.tasks import task

from .sync import sync_repositories


@task
async def sync_repositories_task(github_id, token):
    await sync_repositories(github_id, token)