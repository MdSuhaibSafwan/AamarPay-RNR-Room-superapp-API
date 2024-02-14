import threading
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from services.customize_response import customize_response
from services.exception_handler import exception_handler
from rest_framework.exceptions import ValidationError
from services.constants import ErrorTypes
from core.renderers import CustomJSONRenderer
from requests.exceptions import RequestException
from django.http import Http404
from .models import (
    PGPaymentRequestLog
)
from .serializers import (
    PaymentInitiateSerializer
)
from .payment_gateway_utils import PaymentGatewayPaymentManager


class PaymentInitiateGenericAPIView(GenericAPIView):
    serializer_class = PaymentInitiateSerializer
    renderer_classes = [CustomJSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pg_response = PaymentGatewayPaymentManager.pg_payment_initiate(
                request,
                **serializer.validated_data
            )
            response = Response(
                data=pg_response
            )
            return customize_response(
                response,
                'redriection url after payment initiation'
            )
        except RequestException as excpt:
            return exception_handler(
                exc=excpt,
                message='connection error to PG',
                error_type=ErrorTypes.NETWORK_ERROR.value
            )
        except ValidationError as excpt:
            return exception_handler(
                exc=excpt,
                message='Payment Initiate failure due to validation errors',
                error_type=ErrorTypes.FORM_FIELD_ERROR.value
            )


class PaymentSuccessGenericAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    renderer_classes = [CustomJSONRenderer]

    def post(self, request, *args, **kwargs):
        try:
            mer_txnid = request.data.get('mer_txnid')
            user_id = request.data.get('opt_a')
            payment_req = PGPaymentRequestLog.objects.get(tran_id=mer_txnid)
            thread = threading.Thread(
                target=PaymentGatewayPaymentManager.create_payment_objects,
                kwargs={
                    'is_successful': True,
                    'payment_req': payment_req,
                    'user_id': user_id,
                    'request_data': request.data
                }
            )
            thread.start()
            response = Response()
            return customize_response(
                response,
                'payment processing in progress'
            )
        except RequestException as excpt:
            return exception_handler(
                exc=excpt,
                message='connection error to PG Payment Verification',
                error_type=ErrorTypes.NETWORK_ERROR.value
            )
        except Http404 as excpt:
            return exception_handler(
                exc=excpt,
                message='Transaction ID Not Found against this mer_txnid',
                error_type=ErrorTypes.OBJECT_DOES_NOT_EXIST.value
            )


class PaymentFailureGenericAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    renderer_classes = [CustomJSONRenderer]

    def post(self, request, *args, **kwargs):
        try:
            mer_txnid = request.data.get('mer_txnid')
            user_id = request.data.get('opt_a')
            payment_req = PGPaymentRequestLog.objects.get(tran_id=mer_txnid)
            thread = threading.Thread(
                target=PaymentGatewayPaymentManager.create_payment_objects,
                kwargs={
                    'is_successful': False,
                    'payment_req': payment_req,
                    'user_id': user_id,
                    'request_data': request.data
                }
            )
            thread.start()
            response = Response()
            return customize_response(response, 'payment failure')
        except RequestException as excpt:
            return exception_handler(
                exc=excpt,
                message='connection error to PG Payment Verification',
                error_type=ErrorTypes.NETWORK_ERROR.value
            )
        except Http404 as excpt:
            return exception_handler(
                exc=excpt,
                message='Transaction ID Not Found against this mer_txnid',
                error_type=ErrorTypes.OBJECT_DOES_NOT_EXIST.value
            )


class PaymentCancelGenericAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    renderer_classes = [CustomJSONRenderer]

    def get(self, request, *args, **kwarsg):
        response = Response()
        return customize_response(response, 'payment cancelled')
