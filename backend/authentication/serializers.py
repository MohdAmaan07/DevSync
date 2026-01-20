from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'github_username', 'portfolio_slug', 'theme_preference', 'dark_mode', 'is_portfolio_public']
    

class UserLogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()