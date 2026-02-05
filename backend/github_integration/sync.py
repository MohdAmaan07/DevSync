import httpx
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import GithubProfile, GitHubSyncLog, Repository, Commit


class GithubAPIClient:
    def __init__(self, token):
        self.token = token
        self.base_url = settings.GITHUB_BASE_URL
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def _handle_response(self, response):
        if response.status_code == 200:
            return response.json(), None

        error_msg = response.text[:500]
        if response.status_code == 403 and "rate limit" in error_msg.lower():
            reset_time = response.headers.get("x-rateLimit-reset")
            error_msg = f"Rate limit exceeded. Reset at {reset_time}"
        elif response.status_code == 429:
            reset_time = response.headers.get("x-rateLimit-reset")
            error_msg = f"Too many requests. Reset at {reset_time}"
        return None, {"status_code": response.status_code, "error": error_msg}

    async def fetch_all(self, url, params=None):
        results = []
        errors = []
        async with httpx.AsyncClient() as client:
            current_url = url
            current_params = params
            while current_url:
                try:
                    resp = await client.get(
                        current_url, headers=self.headers, params=current_params
                    )
                    data, error = await self._handle_response(resp)

                    if error:
                        errors.append({"url": current_url, **error})
                        break

                    results.extend(data)
                    current_url = resp.links.get("next", {}).get("url")
                    current_params = None
                except Exception as e:
                    errors.append({"url": current_url, "error": str(e)})
                    break
        return results, errors


class GithubSyncService:
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.client = GithubAPIClient(token)
        self.profile = None

    async def _load_profile(self):
        if not self.profile:
            self.profile = await GithubProfile.objects.filter(
                user_id=self.user_id
            ).afirst()
        return self.profile

    def _save_repo_data(self, repo_data):
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
            github_profile=self.profile,
            github_id=repo_data.get("id"),
            defaults=repo_defaults,
        )

    def _save_commit_data(self, commit_data, repo):
        commit_info = commit_data.get("commit", {})
        author_info = commit_info.get("author", {})

        commit_defaults = {
            "message": commit_info.get("message", "")[:1000],
            "date": parse_datetime(author_info.get("date"))
        }

        Commit.objects.update_or_create(
            repository=repo,
            sha=commit_data["sha"],
            defaults={"github_profile": self.profile, **commit_defaults},
        )

    async def _save_to_db(self, items, save_func):
        def wrapper():
            count = 0
            item_errors = []
            with transaction.atomic():
                for item in items:
                    try:
                        save_func(item)
                        count += 1
                    except Exception as e:
                        item_errors.append({"item": str(item), "error": str(e)})
            return count, item_errors

        return await sync_to_async(wrapper)()

    async def _run_sync_with_log(self, sync_type, sync_coroutine):
        profile = await self._load_profile()
        if not profile:
            return 0, [{"error": "Profile not found"}]

        log = await GitHubSyncLog.objects.acreate(
            github_profile=profile,
            sync_type=sync_type,
            status="pending",
        )

        start_time = timezone.now()
        items_synced = 0
        all_errors = []

        try:
            items_synced, all_errors = sync_coroutine

            if all_errors and items_synced == 0:
                log.status = "failed"
            elif all_errors:
                log.status = "partial"
            else:
                log.status = "success"

        except Exception as e:
            all_errors.append({"error": f"Critical System Error: {str(e)}"})
            log.status = "failed"

        finally:
            completed_at = timezone.now()
            log.completed_at = completed_at
            log.duration = completed_at - start_time

            if sync_type == "repositories":
                log.repos_synced = items_synced
            else:
                log.commits_synced = items_synced

            log.errors = all_errors[:50]
            await log.asave()

        return items_synced, all_errors

    async def sync_repositories(self):
        async def work():
            url = f"{self.client.base_url}/user/repos"
            data, errors = await self.client.fetch_all(url, {"per_page": 100})
            count, db_errors = await self._save_to_db(data, self._save_repo_data)
            errors.extend(db_errors)
            return count, errors

        return await self._run_sync_with_log("repositories", await work())

    async def sync_commits(self, repo):
        async def work():
            url = f"{self.client.base_url}/repos/{repo.full_name}/commits"
            params = {"author": self.profile.github_username, "per_page": 100}
            data, errors = await self.client.fetch_all(url, params)
            count, db_errors = await self._save_to_db(
                data, lambda d: self._save_commit_data(d, repo)
            )
            errors.extend(db_errors)
            return count, errors

        return await self._run_sync_with_log("commits", await work())

    async def sync_all(self):
        repos_synced, repo_errors = await self.sync_repositories()

        if repos_synced == 0:
            return {"repositories": {"synced": 0, "errors": repo_errors}}

        repos = await sync_to_async(list)(
            Repository.objects.filter(github_profile=self.profile)
        )

        total_commits_synced = 0
        all_commit_errors = []

        for repo in repos:
            commits_synced, commit_errors = await self.sync_commits(repo)
            total_commits_synced += commits_synced
            all_commit_errors.extend(
                [{"repo": repo.full_name, **err} for err in commit_errors]
            )

        return {
            "repositories": {"synced": repos_synced, "errors": repo_errors},
            "commits": {"synced": total_commits_synced, "errors": all_commit_errors},
        }
