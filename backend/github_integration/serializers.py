from rest_framework import serializers


class SyncNowResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
