import requests
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import (RNRSearchDestinationSerializer, RNRPropertySearchSerializer,
                          RNRPropertyRoomsAvailabilitySerializer, RNRRoomReservationSerializer,
                          RNRRoomReservationConfirmSerializer, RNRRoomCompareSerializer, ReservationRefundSerializer,
                          RNRRoomCancelReservationSerializer)
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from ..adapters import RNRRoomsAdapter
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.viewsets import ModelViewSet
from .permissions import RNRRoomComparePermission, IsAuthenticated
from ..utils import structure_api_data_or_send_validation_error
from .renderer import RNRAPIJSONRenderer
from ..models import RNRRoomReservation


class RNRSearchDesinationAPIView(APIView):
    serializer_class = RNRSearchDestinationSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRPropertySearchAPIView(APIView):
    serializer_class = RNRPropertySearchSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        self.check_permissions(request=self.request)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRGetPropertyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def get(self, *args, **kwargs):
        rnr_property_id = kwargs.get("rnr_property_id")
        self.check_permissions(request=self.request)
        adapter = RNRRoomsAdapter()
        data = adapter.rnr_get_property_profile(rnr_property_id)
        data = structure_api_data_or_send_validation_error(
            data, raise_exception=True)
        return Response(data=data, status=status.HTTP_200_OK)


class RNRSearchPropertyAvailableRooms(APIView):
    serializer_class = RNRPropertyRoomsAvailabilitySerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        self.check_permissions(request=self.request)
        property_id = kwargs.get("rnr_property_id")
        serializer.context["property_id"] = property_id
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRReserveRoomHoldAPIView(APIView):
    serializer_class = RNRRoomReservationSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        self.check_permissions(request=self.request)
        serializer.is_valid(raise_exception=True)
        serializer.context["request"] = self.request
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class RNRConfirmReservationAPIView(APIView):
    serializer_class = RNRRoomReservationConfirmSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        self.check_permissions(request=self.request)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


class CancelReservationAPIView(APIView):
    serializer_class = RNRRoomCancelReservationSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [RNRAPIJSONRenderer, ]

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        self.check_permissions(request=self.request)
        serializer.is_valid(raise_exception=True)
        data = serializer.request_to_rnr_api()
        return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=["POST", ])
@permission_classes([IsAuthenticated, ])
@renderer_classes([RNRAPIJSONRenderer, ])
def compare_rnr_rooms_api_view(request):
    serializer = RNRRoomCompareSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.make_rnr_request_with_validated_data(
        raise_exception=True)

    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET", ])
@permission_classes([IsAuthenticated, ])
@renderer_classes([RNRAPIJSONRenderer, ])
def user_reserve_rooms_history_api_view(request, user):
    qs = RNRRoomReservation.objects.filter(user=user).order_by("-date_created")
    serializer = RNRRoomReservationSerializer(qs, many=True)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)
