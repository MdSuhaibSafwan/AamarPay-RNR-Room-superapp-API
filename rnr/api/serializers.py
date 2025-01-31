import re
from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from ..adapters import RNRRoomsAdapter, AamarpayPgAdapter
from ..models import RNRRoomReservation
from ..utils import structure_api_data_or_send_validation_error
from django.utils import timezone


class RNRPropertySearchSerializer(serializers.Serializer):
    destination_type = serializers.CharField()
    destination_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError(
                "Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError(
                "Check out date cannot be more than check in date")

        return attrs

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_search_properties(self.validated_data)
        if data.get("success") is not True:
            raise serializers.ValidationError(data.get("api_data"))

        return structure_api_data_or_send_validation_error(data, raise_exception=True)

    def validate_check_in(self, val):
        now = timezone.now().date()
        if now > val:
            raise serializers.ValidationError(
                "Check in cannot be more than today")

        return val

    def validate_check_out(self, val):
        now = timezone.now().date()
        if now > val:
            raise serializers.ValidationError(
                "Check out cannot be more than today")

        return val


class RNRSearchDestinationSerializer(serializers.Serializer):
    destination = serializers.CharField(required=True)

    def request_to_rnr_api(self):
        destination = self.validated_data["destination"]
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_search_destination(destination)
        return structure_api_data_or_send_validation_error(data, raise_exception=True)


class RNRPropertyRoomsAvailabilitySerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()

        self.validated_data["property_id"] = self.context.get("property_id")
        data = rnr_adapter.rnr_check_available_property_rooms(
            self.validated_data)
        return structure_api_data_or_send_validation_error(data, raise_exception=True)

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError(
                "Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError(
                "Check out date cannot be more than check in date")

        return attrs

    def validate_check_in(self, val):
        now = timezone.now().date()
        if now > val:
            raise serializers.ValidationError(
                "Check in cannot be more than today")

        return val

    def validate_check_out(self, val):
        now = timezone.now().date()
        if now > val:
            raise serializers.ValidationError(
                "Check out cannot be more than today")

        return val


class RNRRoomReservationSerializer(serializers.Serializer):
    user = serializers.CharField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    property_id = serializers.IntegerField()
    rooms = serializers.ListField()
    is_active = serializers.SerializerMethodField()
    guest_name = serializers.CharField(required=True)
    guest_email = serializers.CharField(required=True)
    guest_mobile_no = serializers.CharField(required=True)
    guest_address = serializers.CharField(required=True)
    guest_special_request = serializers.CharField(required=False)

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()  # initialized rnr adapter
        # getting current authenticated user from request
        # self.validated_data["user"] = self.context.get("request").user
        # reserving rooms from validated data
        data = rnr_adapter.rnr_reserve_rooms(self.validated_data)
        self.add_room_details_to_reservation(data)

        return structure_api_data_or_send_validation_error(data, raise_exception=True)

    def add_room_details_to_reservation(self, data):
        success = data.get("success", None)
        if not success:
            return None
        reservation_id = data["api_data"]["data"]["id"]
        reservation_obj = RNRRoomReservation.objects.get(
            reservation_id=reservation_id)
        room_details = data["api_data"]["data"]["rooms_details"]
        reservation_obj.rooms = room_details
        reservation_obj.save()
        return reservation_obj

    def get_is_active(self, serializer):
        return serializer.is_active

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError(
                "Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError(
                "Check out date cannot be more than check in date")

        return attrs

    def validate_guest_mobile_no(self, val):
        matches = re.findall("^01[3-9]\d{8}", val)
        print("Matches ", matches)
        if matches.__len__() < 1:
            raise serializers.ValidationError("provide correct phone format")
        val = "+88" + val
        # print("Phone number ", val)
        return val

    def validate_guest_name(self, value):
        matches = re.findall("[A-Za-z]", value)
        if len(matches) < 1:
            raise serializers.ValidationError("Invalid name provided")

        return value

    def validate_guest_email(self, val):
        # checking email format via regular expression
        matches = re.findall("\w+@\w+[.]com", val)
        if matches.__len__() < 1:
            raise serializers.ValidationError("provide correct email format")
        return val

    def validate_rooms(self, rooms):
        for room in rooms:
            room_id = room.get("id")
            room_quantity = int(room.get("quantity"))
            if room_quantity <= 0:
                raise serializers.ValidationError(
                    "Room Quantity cannot be less than 1")

        return rooms

    def validate_check_in(self, val):
        now = timezone.now().date()
        if now > val:
            raise serializers.ValidationError(
                "Check in cannot be more than today")

        return val

    def validate_check_out(self, val):
        now = timezone.now().date()
        if now > val:
            raise serializers.ValidationError(
                "Check out cannot be more than today")

        return val


class RNRRoomReservationConfirmSerializer(serializers.Serializer):
    reservation_id = serializers.CharField(required=True)
    mer_txid = serializers.CharField(required=True)

    def request_to_rnr_api(self):
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_confirm_reservation(self.validated_data.get(
            "reservation_id"), self.validated_data.get("mer_txid"))
        return structure_api_data_or_send_validation_error(data, raise_exception=True)

    def validate(self, attrs):
        reservation_id = attrs["reservation_id"]
        # mer_txid = attrs["mer_txid"]
        # pg = AamarpayPgAdapter()
        # pg_verification_data = pg.verify_transaction(mer_txid, reservation_id)
        # # verifying transaction and getting an object
        # verified = pg_verification_data.get("verified")
        # if not verified:
        #     raise serializers.ValidationError(pg_verification_data)

        return super().validate(attrs)


class RNRRoomCompareSerializer(serializers.Serializer):
    property_id = serializers.CharField()
    rooms = serializers.ListField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate_check_in(self, value):
        now = timezone.now()
        if value < now.date():
            raise serializers.ValidationError(
                "Check in date cannot be less than today")

        return value

    def validate(self, attrs):
        c_in = attrs["check_in"]
        c_out = attrs["check_out"]
        if c_in == c_out:
            raise serializers.ValidationError(
                "Check in and checkout date cannot be same")

        if c_out < c_in:
            raise serializers.ValidationError(
                "Check out date cannot be more than check in date")

        return attrs

    def make_rnr_request_with_validated_data(self, raise_exception=False):
        data = self.validated_data
        # frontend will provide a list of rooms
        rooms_filter = data.pop("rooms")
        adapter = RNRRoomsAdapter()
        data = adapter.rnr_check_available_property_rooms(
            data)  # checking if the rooms are available
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
                # if there is any extra room provided we are returning an error
                raise serializers.ValidationError(
                    f"Rooms with id {rooms_filter} not found")

        data["api_data"]["data"]["rooms"] = filtered_rooms_list
        data["api_data"]["data"]["total"] = len(filtered_rooms_list)

        return structure_api_data_or_send_validation_error(data, raise_exception=True)


class ReservationRefundSerializer(serializers.Serializer):
    reservation_id = serializers.CharField()

    def validate_reservation_id(self, value):
        qs = RNRRoomReservation.objects.filter(reservation_id=value)
        if not qs.exists():
            raise serializers.ValidationError("Reservation not found")

        return value

    def request_rnr_api(self):
        adapter = RNRRoomsAdapter()
        # adding to refund table with validated data
        data = adapter.ask_for_refund(self.validated_data)
        return structure_api_data_or_send_validation_error(data, raise_exception=True)


class RNRRoomCancelReservationSerializer(serializers.Serializer):
    reservation_id = serializers.CharField()

    def validate_reservation_id(self, value):
        qs = RNRRoomReservation.objects.filter(reservation_id=value)
        if not qs.exists():
            raise serializers.ValidationError("Reservation not found")

        return value

    def request_to_rnr_api(self):
        adapter = RNRRoomsAdapter()
        data = adapter.cancel_reservation(
            self.validated_data)  # canceling a reservation
        return structure_api_data_or_send_validation_error(data, raise_exception=True)
