from rest_framework import serializers

from github_integration.models import GithubProfile, Repository


class GithubProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubProfile
        fields = '__all__'

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'

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
    repository_details = RepositorySerializer(allow_null=True, many=True)