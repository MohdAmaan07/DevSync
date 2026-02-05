from django.tasks import task
from asgiref.sync import sync_to_async
from .sync import GithubSyncService
from .models import Repository


@task
async def sync_repositories_task(user_id, token):
    service = GithubSyncService(user_id, token)
    result = await service.sync_repositories()
    return result


@task
async def sync_commits_task(user_id, token):
    service = GithubSyncService(user_id, token)
    await service._load_profile()
    
    repos = await sync_to_async(list)(
        Repository.objects.filter(github_profile=service.profile)
    )
    
    total_synced = 0
    all_errors = []
    
    for repo in repos:
        count, errors = await service.sync_commits(repo)
        total_synced += count
        all_errors.extend(errors)
    
    return {"synced": total_synced, "errors": all_errors}


@task
async def sync_all_task(user_id, token):
    service = GithubSyncService(user_id, token)
    result = await service.sync_all()
    return result
