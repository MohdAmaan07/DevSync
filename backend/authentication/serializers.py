from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "github_username",
        ]

class UserLogoutRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class UserLogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class GitHubDisconnectRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class GitHubDisconnectResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class AuthTokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()