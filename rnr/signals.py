from rnr.models import (
    UserRoomPurchaseConfirmResponseLog
)
from .adapters import (
    RNRRoomsAdapter
)
from payment.models import UserTransaction
from django.contrib.auth import get_user_model
from django.conf import settings
from django.dispatch import receiver
from .models import RNRAccessToken
from django.db.models.signals import post_save
from django.db.models import Q

User = get_user_model()


@receiver(signal=post_save, sender=RNRAccessToken)
def make_all_other_rnr_access_token_expired_other_than_this(sender, instance, created, **kwargs):
    if created:
        qs = RNRAccessToken.objects.filter(~Q(id=instance.id), expired=False)
        qs.update(expired=True)


@receiver(signal=post_save, sender=UserTransaction)
def make_request_to_rnr_room_to_confirm_room_purchase(sender, instance: UserTransaction, created, **kwargs):
    if created and instance.payment_verification_response.status_title == 'Successful Transaction':
        purchase_history_instance = instance.payment_verification_response.pg_response.pg_payment_request.purchase_history_pg_payment_request
        rnr_adapter = RNRRoomsAdapter()
        data = rnr_adapter.rnr_confirm_reservation(
            purchase_history_instance.reservation_id,
            instance.payment_verification_response.pg_response.pg_payment_request.tran_id,
            instance.payment_verification_response.pg_response.pg_txnid[0]
        )
        UserRoomPurchaseConfirmResponseLog.objects.create(
            api_response=data,
            user_transaction=instance
        )
        if data.get('api_data')['status'] == 'Succeed':
            purchase_history_instance.mark_purchase_successful()
