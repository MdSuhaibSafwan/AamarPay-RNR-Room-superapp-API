import requests
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import (RNRSearchDestinationSerializer, RNRPropertySearchSerializer,
            RNRPropertyRoomsAvailabilitySerializer, )
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from ..adapters import RNRRoomsAdapter
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied


class RNRSearchDesinationAPIView(APIView):
    serializer_class = RNRSearchDestinationSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RNRPropertySearchAPIView(APIView):
    serializer_class = RNRPropertySearchSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
