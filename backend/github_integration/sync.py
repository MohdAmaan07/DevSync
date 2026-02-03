import httpx
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import GithubProfile, GitHubSyncLog, Repository


async def fetch_github_repositories(token):
    repos = []
    errors = []
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"{settings.GITHUB_API_BASE_URL}/user/repos?per_page=100"

    async with httpx.AsyncClient() as client:
        while url:
            try:
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    error_msg = response.text[:500]
                    if (
                        response.status_code == 403
                        and "rate limit" in error_msg.lower()
                    ):
                        reset_time = response.headers.get("x-rateLimit-reset")
                        error_msg = f"Rate limit exceeded. Reset at {reset_time}"
                    elif response.status_code == 429:
                        reset_time = response.headers.get("x-rateLimit-reset")
                        error_msg = f"Too many requests. Reset at {reset_time}"

                    errors.append(
                        {
                            "url": url,
                            "status_code": response.status_code,
                            "error": error_msg,
                        }
                    )
                    break

                repos_data = response.json()
                repos.extend(repos_data)

                next_link = response.links.get("next")
                url = next_link["url"] if next_link else None

            except Exception as e:
                errors.append({"url": url, "error": str(e)})
                break

    return repos, errors


def save_to_db(repos, github_profile):
    count = 0
    item_errors = []

    with transaction.atomic():
        for repo_data in repos:
            try:
                repo_defaults = {
                    "name": repo_data.get("name"),
                    "full_name": repo_data.get("full_name"),
                    "description": repo_data.get("description"),
                    "github_id": repo_data.get("id"),
                    "html_url": repo_data.get("html_url"),
                    "clone_url": repo_data.get("clone_url"),
                    "git_url": repo_data.get("git_url"),
                    "stars_count": repo_data.get("stargazers_count", 0),
                    "forks_count": repo_data.get("forks_count", 0),
                    "watchers_count": repo_data.get("watchers_count", 0),
                    "open_issues_count": repo_data.get("open_issues_count", 0),
                    "language": repo_data.get("language"),
                    "is_private": repo_data.get("private", False),
                    "is_fork": repo_data.get("fork", False),
                    "is_archived": repo_data.get("archived", False),
                    "created_at_github": parse_datetime(repo_data.get("created_at"))
                    if repo_data.get("created_at")
                    else None,
                    "updated_at_github": parse_datetime(repo_data.get("updated_at"))
                    if repo_data.get("updated_at")
                    else None,
                    "pushed_at_github": parse_datetime(repo_data.get("pushed_at"))
                    if repo_data.get("pushed_at")
                    else None,
                }

                Repository.objects.update_or_create(
                    github_profile=github_profile,
                    github_id=repo_data.get("id"),
                    defaults=repo_defaults,
                )
                count += 1
            except Exception as e:
                item_errors.append(
                    {"repo": repo_data.get("full_name", "Unknown"), "error": str(e)}
                )

    return count, item_errors


async def sync_repositories(user_id, token):
    github_profile = await GithubProfile.objects.filter(user_id=user_id).afirst()

    if not github_profile:
        return 0

    sync_log = await GitHubSyncLog.objects.acreate(
        github_profile=github_profile,
        sync_type="repositories",
        status="pending",
    )

    started_at = timezone.now()
    repos_synced = 0
    all_errors = []

    try:
        repos, fetch_errors = await fetch_github_repositories(token)
        all_errors.extend(fetch_errors)

        if repos:
            repos_synced, db_errors = await sync_to_async(save_to_db)(
                repos, github_profile
            )
            all_errors.extend(db_errors)

        if all_errors and repos_synced == 0:
            sync_log.status = "failed"
        elif all_errors and repos_synced > 0:
            sync_log.status = "partial"
        else:
            sync_log.status = "success"

    except Exception as e:
        all_errors.append({"error": str(e)})
        sync_log.status = "failed"

    finally:
        completed_at = timezone.now()
        sync_log.completed_at = completed_at
        sync_log.duration = completed_at - started_at
        sync_log.repos_synced = repos_synced
        sync_log.errors = all_errors
        await sync_log.asave()

    return repos_synced
