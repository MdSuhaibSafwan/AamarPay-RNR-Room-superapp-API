from django.urls import reverse
import json
import uuid
import time
from .models import (
    PGPaymentRequestLog,
    PGPaymentResponseLog,
    PGPaymentVerificationResponseLog,
    UserTransaction
)
from services.constants import RequestTypes
from .payment_gateway_config import (
    PAYLOAD,
    PAYMENT_GATEWAY_URL,
    PAYMENT_VERIFICATOION_URL
)
from services.helper_functions import (
    RequestMixin
)
from rnr.models import UserRoomPurchaseHistory


class PaymentGatewayPaymentManager:
    api_url = PAYMENT_GATEWAY_URL
    payload = PAYLOAD
    payment_verification_url = PAYMENT_VERIFICATOION_URL

    @staticmethod
    def verify_payment(payment_req: PGPaymentRequestLog):
        payload = {
            'request_id': payment_req.tran_id,
            'store_id': payment_req.store_id,
            'signature_key': PaymentGatewayPaymentManager.payload.get('signature_key'),
            'type': PaymentGatewayPaymentManager.payload.get('type')
        }
        req_context = {
            'req_type': RequestTypes.POST,
            'url': PaymentGatewayPaymentManager.payment_verification_url,
            'payload': payload,
            'payload_type': 'data'
        }
        res = RequestMixin.make_request(**req_context)
        return res.json()

    @staticmethod
    def create_payment_objects(is_successful, payment_req, user_id, request_data):
        try:
            pg_response = PGPaymentResponseLog.objects.create(
                is_successful=is_successful,
                pg_payment_request=payment_req,
                **request_data
            )
            pg_verified_data = PaymentGatewayPaymentManager.verify_payment(
                payment_req=payment_req)
            pg_payment_verification_res = PGPaymentVerificationResponseLog.objects.create(
                pg_response=pg_response,
                **pg_verified_data
            )
            user_transaction = UserTransaction.objects.create(
                payment_verification_response=pg_payment_verification_res,
                user_id=user_id
            )
            return user_transaction
        except Exception as excpt:
            return excpt

    @staticmethod
    def get_unique_tran_id():
        unique_id = str(uuid.uuid4().int)[:32]
        timestamp = int(time.time())
        tran_id = f"{unique_id}{timestamp}"
        tran_id = tran_id[:32]
        return tran_id

    @staticmethod
    def pg_payment_initiate(request, **kwargs):
        if request.is_secure():
            base_url = request.build_absolute_uri('/').rstrip('/')
        else:
            base_url = request.build_absolute_uri(
                '/').rstrip('/').replace('http://', 'https://')

        PaymentGatewayPaymentManager.payload.update({
            'opt_a': kwargs.get('user_id'),
            'tran_id': PaymentGatewayPaymentManager.get_unique_tran_id(),
            'amount': str(kwargs.get('amount')),
            'cus_name': kwargs.get('cus_name'),
            'cus_email': kwargs.get('cus_email'),
            'cus_phone': kwargs.get('cus_phone'),
            'success_url': base_url + reverse('payment-success'),
            'fail_url': base_url + reverse('payment-failure'),
            'cancel_url': base_url + reverse('payment-cancelled'),
            'desc': kwargs.get('desc'),
        })
        req_context = {
            'req_type': RequestTypes.POST,
            'url': PaymentGatewayPaymentManager.api_url,
            'payload': PaymentGatewayPaymentManager.payload,
        }
        res = RequestMixin.make_request(**req_context)
        if res.status_code == 200:
            pg_payment_request_log = PGPaymentRequestLog.objects.create(
                **PaymentGatewayPaymentManager.payload
            )
            UserRoomPurchaseHistory.objects.create(
                pg_payment_request_log=pg_payment_request_log,
                reservation_id=kwargs.get('reservation_id'),
            )
        payment_url = json.loads(res.content).get('payment_url')
        return payment_url
