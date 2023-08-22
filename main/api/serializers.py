import json
import requests
from ..models import RNRUser, RNRAccessToken
from rest_framework import serializers
from django.conf import settings

class RNRUserSerializer(serializers.ModelSerializer):
    rnr_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RNRAccessToken
        read_only_fields = ["token", "token_type", "expired", "expire_time"]
        fields = "__all__"


class RNRUserAuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        url = "{}/api-b2b/v1/identity/token/grant".format(settings.RNR_BASE_URL)
        headers = {
            "Content-Type": "application/json",
            "Access": "application/json",
            "x-api-key": settings.RNR_API_KEY,
            "x-api-secret": settings.RNR_API_SECRET_KEY,
        }
        payload = json.dumps({
            "username": validated_data.get("username"),
            "password": validated_data.get("password")
        })
        r = requests.post(url, headers=headers, data=payload)
        if r.status_code != 200:
            raise serializers.ValidationError(r.json())
        
        resp_data = r.json()
        return resp_data["data"]
