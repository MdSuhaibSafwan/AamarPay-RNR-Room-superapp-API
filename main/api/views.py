import requests
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from .serializers import RNRUserAuthenticationSerializer, RNRAccessTokenSerializer
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


class UserAuthenticationAPIView(CreateAPIView):
    serializer_class = RNRUserAuthenticationSerializer

    def create(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        rnr_access_obj = serializer.save()
        serializer = RNRAccessTokenSerializer(rnr_access_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)