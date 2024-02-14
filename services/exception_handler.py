import json
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import exceptions
from rest_framework.response import Response
from requests.exceptions import (
    RequestException,
    ConnectTimeout,
    ConnectionError,
    Timeout
)
from services.constants import ErrorTypes
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist


def exception_handler(exc: Exception, context=None, message=None, error_type=None):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, MultipleObjectsReturned):
        data = {
            'detail': "The query returned multiple objects when only one was expected.",
            'error_type': error_type,
            'message': message
        }
        return Response(data, status=status.HTTP_409_CONFLICT)

    if isinstance(exc, json.JSONDecodeError):
        data = {
            'detail': "json decoder error",
            'error_type': error_type,
            'message': message
        }
        return Response(data, status=status.HTTP_409_CONFLICT)

    if isinstance(exc, ObjectDoesNotExist):
        data = {
            'detail': "Object doesn't exist",
            'error_type': error_type,
            'message': message
        }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, RequestException):
        if isinstance(exc, ConnectTimeout):
            error_message = 'Connection to the payment gateway timed out. Please try again later.'
        elif isinstance(exc, ConnectionError):
            error_message = 'Failed to establish a connection to the payment gateway. Please check your internet connection and try again.'
        elif isinstance(exc, Timeout):
            error_message = 'The request to the payment gateway timed out. Please try again later.'
        else:
            error_message = 'A network error occurred while connecting to the payment gateway. Please try again later.'
        return Response(
            {
                'detail': error_message,
                'error_type': ErrorTypes.NETWORK_ERROR.value,
                'message': 'Network Error'
            },
            status=500
        )

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait
        if isinstance(exc, exceptions.NotAuthenticated):
            data = {
                'detail': exc.detail,
                'error_type': ErrorTypes.NOT_AUTHENTICATED.value,
                'message': 'Not Authenticated'
            }
        if isinstance(exc, exceptions.PermissionDenied):
            data = {
                'detail': exc.detail,
                'error_type': ErrorTypes.NOT_AUTHORIZED.value,
                'message': 'Not Authorized'
            }
        else:
            data = {
                'detail': exc.detail,
                'error_type': error_type,
                'message': message
            }
        return Response(data, status=exc.status_code, headers=headers)

    return None
