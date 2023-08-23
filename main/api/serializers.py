from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from ..adapters import RNRRoomsAdapter


class RNRPropertySearchSerializer(serializers.Serializer):
    destination_type = serializers.CharField()
    destination_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError("Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError("Check out date cannot be more than check in date")
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_search_properties(attrs)
        if data.get("success") is not True:
            raise serializers.ValidationError(data.get("api_data"))
        
        return data
    
    def validate_check_in(self, val):
        now = timezone.now().date()
        if now > val:   
            raise serializers.ValidationError("Check in cannot be more than today")

        return val

    def validate_check_out(self, val):
        now = timezone.now().date()
        if now > val:   
            raise serializers.ValidationError("Check out cannot be more than today")

        return val


class RNRSearchDestinationSerializer(serializers.Serializer):
    destination = serializers.CharField(required=True)

    def validate(self, attrs):
        destination = attrs["destination"]
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_search_destination(destination)
        succeeded = data.get("success", False)
        if not succeeded:
            raise serializers.ValidationError(data.get("api_data"))

        return data


class RNRPropertyRoomsAvailabilitySerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError("Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError("Check out date cannot be more than check in date")
        rnr_adapter = RNRRoomsAdapter()

        attrs["property_id"] = self.context.get("property_id")
        data = rnr_adapter.rnr_check_available_property_rooms(attrs)
        if data.get("success") is not True:
            raise serializers.ValidationError(data.get("api_data"))
        
        return data
    
    def validate_check_in(self, val):
        now = timezone.now().date()
        if now > val:   
            raise serializers.ValidationError("Check in cannot be more than today")

        return val

    def validate_check_out(self, val):
        now = timezone.now().date()
        if now > val:   
            raise serializers.ValidationError("Check out cannot be more than today")

        return val
