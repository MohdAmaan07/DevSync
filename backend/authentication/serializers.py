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


class UserLogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class GitHubDisconnectResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
