import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import GithubProfile, GitHubSyncLog, Repository


def sync_repositories(user_id, token):
    github_profile = GithubProfile.objects.filter(user_id=user_id).first()

    if not github_profile:
        return 0

    sync_log = GitHubSyncLog.objects.create(
        github_profile=github_profile,
        sync_type="repositories",
        status="failed",
    )

    started_at = sync_log.started_at
    repos_synced = 0
    errors = []

    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        url = "https://api.github.com/user/repos?per_page=100"

        while url:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                errors.append(
                    {
                        "url": url,
                        "status_code": response.status_code,
                        "response": response.text[:500],
                    }
                )
                break

            repos_data = response.json()

            for repo_data in repos_data:
                repo = {
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

                try:
                    Repository.objects.update_or_create(
                        github_profile=github_profile,
                        name=repo_data.get("name"),
                        defaults=repo,
                    )
                    repos_synced += 1

                except Exception as e:
                    errors.append({"repo": repo_data.get("full_name"), "error": str(e)})

            next_link = response.links.get("next")
            url = next_link["url"] if next_link else None

        if errors and repos_synced == 0:
            sync_log.status = "failed"
        elif errors and repos_synced > 0:
            sync_log.status = "partial"
        else:
            sync_log.status = "success"

    except Exception as e:
        errors.append({"error": str(e)})
        sync_log.status = "failed"

    finally:
        completed_at = timezone.now()
        sync_log.completed_at = completed_at
        sync_log.duration = completed_at - started_at
        sync_log.repos_synced = repos_synced
        sync_log.errors = errors
        sync_log.save()

    return repos_synced
