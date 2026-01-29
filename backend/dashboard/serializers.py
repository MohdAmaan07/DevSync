from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from github_integration.models import GithubProfile, Repository


class GithubProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubProfile
        exclude = ("id", "user", "access_token")


class RepositorySerializer(serializers.ModelSerializer):
    topics = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    class Meta:
        model = Repository
        exclude = ("id", "github_profile")


class DashboardRequestSerializer(serializers.Serializer):
    repository_count = serializers.IntegerField(
        required=False, min_value=1, max_value=100, default=6
    )


class DashboardResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    github_username = serializers.CharField(max_length=255, allow_null=True)
    theme_preference = serializers.CharField(max_length=50)
    dark_mode = serializers.BooleanField()
    is_portfolio_public = serializers.BooleanField()
    portfolio_slug = serializers.SlugField(max_length=255)
    github_profile = GithubProfileSerializer(allow_null=True)

    repository_details = serializers.SerializerMethodField()

    @extend_schema_field(RepositorySerializer(many=True))
    def get_repository_details(self, obj):
        repositories = Repository.objects.filter(github_profile__user=obj)
        return RepositorySerializer(repositories, many=True).data


class SyncNowResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
