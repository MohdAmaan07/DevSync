from rest_framework.throttling import UserRateThrottle


class GitHubSyncThrottle(UserRateThrottle):
    scope = "github_sync"
