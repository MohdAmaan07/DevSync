from rest_framework import serializers

class DashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    github_username = serializers.CharField(max_length=255, allow_null=True)
    theme_preference = serializers.CharField(max_length=50)
    dark_mode = serializers.BooleanField()
    is_portfolio_public = serializers.BooleanField()
    portfolio_slug = serializers.SlugField(max_length=255)