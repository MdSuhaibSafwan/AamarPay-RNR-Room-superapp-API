import re
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
        
        return attrs
    
    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_search_properties(self.validated_data)
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

    def request_to_rnr_api(self):
        destination = self.validated_data["destination"]
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_search_destination(destination)
        succeeded = data.get("success", False)
        if not succeeded:
            raise serializers.ValidationError(data.get("api_data"))

        return data


class RNRPropertyRoomsAvailabilitySerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()

        self.validated_data["property_id"] = self.context.get("property_id")
        data = rnr_adapter.rnr_check_available_property_rooms(self.validated_data)
        if data.get("success") is not True:
            raise serializers.ValidationError(data.get("api_data"))
        
        return data

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError("Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError("Check out date cannot be more than check in date")
    
        return attrs

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


class RNRRoomReservationSerializer(serializers.Serializer):
    search_id = serializers.IntegerField()
    property_id = serializers.IntegerField()
    rooms = serializers.ListField()
    guest_name = serializers.CharField(required=True)
    guest_email = serializers.CharField(required=True)
    guest_mobile_no = serializers.CharField(required=True)
    guest_address = serializers.CharField(required=True)
    guest_special_request = serializers.CharField(required=False)

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()
        self.validated_data["rooms_details"] = self.validated_data["rooms"]
        del self.validated_data["rooms"]
        self.validated_data["user"] = self.context.get("request").user
        data = rnr_adapter.rnr_reserve_rooms(self.validated_data)
        if data.get("success") is not True:
            raise serializers.ValidationError(data.get("api_data"))
        
        return data

    def validate_guest_mobile_no(self, val):
        matches = re.findall("[+]880\d{10}", val)
        if matches.__len__() < 1:
            raise serializers.ValidationError("provide correct phone format")
        return val

    def validate_guest_email(self, val):
        matches = re.findall("\w+@\w+[.]com", val)
        if matches.__len__() < 1:
            raise serializers.ValidationError("provide correct email format")
        return val


class RNRRoomReservationConfirmSerializer(serializers.Serializer):
    reservation_id = serializers.CharField(required=True)

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_confirm_reservation(self.validated_data.get("reservation_id"))
        if data.get("success") is not True:
            raise serializers.ValidationError(data.get("api_data"))
        return data


class RNRRoomCompareSerializer(serializers.Serializer):
    property_id = serializers.CharField()
    rooms = serializers.ListField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError("Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError("Check out date cannot be more than check in date")
    
        return attrs
    
    def make_rnr_request_with_validated_data(self, raise_exception=False):
        data = self.validated_data
        rooms_filter = data.pop("rooms")
        print("Rooms list " , rooms_filter)
        adapter = RNRRoomsAdapter()
        data = adapter.rnr_check_available_property_rooms(data)
        if raise_exception == True:
            error = data.get("error", False)
            if error is True:
                raise serializers.ValidationError(data.get("api_data")) 
        
        rooms = data.get("api_data").get("data").get("rooms")
        filtered_rooms_list = []
        for room in rooms:
            room_id = int(room.get("id"))
            if room_id in rooms_filter:
                rooms_filter.pop(rooms_filter.index(room_id))
                filtered_rooms_list.append(room)

        if raise_exception == True:
            if rooms_filter.__len__() > 0:
                raise serializers.ValidationError(f"Rooms with id {rooms_filter} not found")
        

        data["api_data"]["data"]["rooms"] = filtered_rooms_list
        data["api_data"]["data"]["total"] = len(filtered_rooms_list)

        return data
