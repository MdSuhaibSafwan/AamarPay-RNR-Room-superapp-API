from enum import Enum


class ErrorTypes(Enum):
    FORM_FIELD_ERROR = 'form_field_error'
    OBJECT_DOES_NOT_EXIST = 'object_not_found'
    INVALID_CREDENTIAL = 'invalid_credential'
    INVALID_REFRESH_TOKEN = 'invalid_refresh_token'
    NOT_AUTHENTICATED = 'not_authenticated'
    NOT_AUTHORIZED = 'not_authorized'
    NETWORK_ERROR = 'network_error'
    MULTIPLE_OBJECT_RETURNED = 'multiple_object_returned'


class RequestTypes(Enum):
    POST = 'POST'
    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
