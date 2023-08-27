import requests
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import (RNRSearchDestinationSerializer, RNRPropertySearchSerializer,
            RNRPropertyRoomsAvailabilitySerializer, RNRRoomReservationSerializer,
            RNRRoomReservationConfirmSerializer, RNRRoomCompareSerializer)
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from ..adapters import RNRRoomsAdapter
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from ..models import RNRRoomCompare
from .permissions import RNRRoomComparePermission


class RNRSearchDesinationAPIView(APIView):
    serializer_class = RNRSearchDestinationSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRPropertySearchAPIView(APIView):
    serializer_class = RNRPropertySearchSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRGetPropertyProfileAPIView(APIView):

    def get(self, *args, **kwargs):
        rnr_property_id = kwargs.get("rnr_property_id")
        adapter = RNRRoomsAdapter()
        data = adapter.rnr_get_property_profile(rnr_property_id)
        if data.get("success") == False:
            raise NotFound(data.get("api_data"))

        return Response(data=data, status=status.HTTP_200_OK)


class RNRSearchPropertyAvailableRooms(APIView):
    serializer_class = RNRPropertyRoomsAvailabilitySerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        property_id = kwargs.get("rnr_property_id")
        serializer.context["property_id"] = property_id
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRReserveRoomHoldAPIView(APIView):
    serializer_class = RNRRoomReservationSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRConfirmReservationAPIView(APIView):
    serializer_class = RNRRoomReservationConfirmSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRRoomCompareViewSet(ModelViewSet):
    serializer_class = RNRRoomCompareSerializer
    permission_classes = [IsAuthenticated, RNRRoomComparePermission, ]

    def get_queryset(self):
        user = self.request.user
        qs = RNRRoomCompare.objects.filter(user=user)
        return qs

    def perform_create(self, serializer):
        serializer.context["request"] = self.request
        return serializer.save()


"""
{
    "search_id": 128,
    "property_id": "2",
    "guest_email": "admin@gmail.com",
    "guest_name": "md",
    "guest_mobile_no": "+8801813507781",
    "guest_address": "dhaka",
    "guest_special_request": "no",
    "rooms": [
        {
            "id": "1",
            "quantity": "2"
        },
        {
            "id": "6773",
            "quantity": "3"
        }
    ]
}


"""
