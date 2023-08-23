import json
import requests
from ..models import RNRAccessToken
from rest_framework import serializers
from django.conf import settings
from django.utils import timezone


class RNRAccessTokenSerializer(serializers.ModelSerializer):
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
        
        data = r.json()["data"]

        return data
    

class RNRPropertySearchValidator(serializers.Serializer):
    destination_type = serializers.CharField()
    destination_id = serializers.IntegerField()
    check_in = serializers.DateField(input_formats="%Y-%m-%d")
    check_out = serializers.DateField(input_formats="%Y-%m-%d")

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError("Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError("Check out date cannot be more than check in date")

        return super().validate(attrs)
    
    def validate_check_in(val):
        now = timezone.now().date()
        if now > val:   
            raise serializers.ValidationError("Check in cannot be more than today")

        return val

    def validate_check_out(val):
        now = timezone.now().date()
        if now > val:   
            raise serializers.ValidationError("Check out cannot be more than today")

        return val
