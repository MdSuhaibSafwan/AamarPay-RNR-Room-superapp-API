import uuid
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from payment.models import PGPaymentRequestLog
from payment.models import UserTransaction

User = get_user_model()


def uuid_without_dash():
    return uuid.uuid4().hex


class RNRAccessToken(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          editable=False, default=uuid_without_dash)
    # rnr_refresh_token = models.ForeignKey(RNRRefreshToken, on_delete=models.CASCADE)
    token = models.CharField(max_length=300, unique=True)
    token_type = models.CharField(max_length=100, null=True)
    expired = models.BooleanField(default=False)
    expire_time = models.FloatField(default=3500.00)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"< Access-Token {self.token}>"

    def has_expired(self):
        if self.expired:
            return self.expired
        t1 = timezone.now()
        t2 = self.created + timedelta(seconds=self.expire_time)
        return t1 > t2


class RNRRoomReservation(models.Model):
    user = models.CharField(max_length=100, blank=False, null=True)
    reservation_id = models.CharField(max_length=2040000)
    property_id = models.CharField(max_length=2040000)
    is_active = models.BooleanField(default=False)
    check_in = models.DateField()
    check_out = models.DateField()
    amount = models.FloatField()
    rooms = models.JSONField(default=dict)
    rnr_transaction_code = models.CharField(max_length=2040, null=True)
    pg_txid = models.CharField(max_length=2040, null=True)
    mer_txid = models.CharField(max_length=2040, null=True)
    currency = models.CharField(max_length=3)

    guest_name = models.CharField(max_length=500, null=True)
    guest_email = models.CharField(max_length=500, null=True)
    guest_mobile_no = models.CharField(max_length=50, null=True)
    guest_address = models.CharField(max_length=500, null=True)
    guest_special_request = models.CharField(max_length=500, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reservation_id)


class RNRRoomReservationRefund(models.Model):
    reservation = models.OneToOneField(
        RNRRoomReservation, on_delete=models.CASCADE, )
    refunded = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reservation.reservation_id)


class UserRoomPurchaseHistoryManager(models.Manager):
    def create(self, *args, **kwargs):
        model_field_names = [field.name for field in self.model._meta.fields]
        valid_kwargs = {key: value for key,
                        value in kwargs.items() if key in model_field_names}
        subscription_purchase_history = super(UserRoomPurchaseHistoryManager, self).create(
            **valid_kwargs
        )
        return subscription_purchase_history


class UserRoomPurchaseHistory(models.Model):
    class PurchaseStatus(models.TextChoices):
        SUCCESSFUL = "SUCC", _('Successful')
        FAILED = "FAIL", _('Failed')

    pg_payment_request_log = models.OneToOneField(
        to=PGPaymentRequestLog,
        on_delete=models.RESTRICT,
        related_name=_('purchase_history_pg_payment_request'),
        verbose_name=_('pg payment request'),
        unique=True,
        blank=False,
        null=False,
        primary_key=True,
        help_text=_(
            'the pg payment request from which the purchase history was generated'
        ),
        error_messages={
            'null': _('the payment request must be provided'),
            'unique': _('the request instance must be unique')
        }
    )
    reservation_id = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text=_(
            "The Rnr room reservation id that is purchased by this user"
        ),
        error_messages={
            'null': _("The Rnr room reservation id cannot be null")
        },
        verbose_name=_('The Rnr room reservation id'),
    )
    purchase_status = models.CharField(
        max_length=5,
        verbose_name=_('purchase status'),
        null=False,
        blank=False,
        default=PurchaseStatus.FAILED,
        choices=PurchaseStatus.choices,
        help_text=_(
            'The purchase status of the package'),
        error_messages={
            'null': _('purchase status cannot be null')
        }
    )
    purchase_timestamp = models.DateTimeField(
        verbose_name=_('purchase at'),
        auto_now_add=True,
        help_text=_("The timestamp when the purchase was made"),
    )

    objects = UserRoomPurchaseHistoryManager()

    class Meta:
        ordering = ['-purchase_timestamp']
        verbose_name = _('User Room Purchase History')
        verbose_name_plural = _('User Room Purchase Histories')
        db_table_comment = "User Room Purchase History"

    def mark_purchase_successful(self):
        """
        Method to mark the purchase status as successful.
        """
        self.purchase_status = self.PurchaseStatus.SUCCESSFUL
        self.save()


class UserRoomPurchaseConfirmResponseLogManager(models.Manager):
    def create(self, *args, **kwargs):
        model_field_names = [field.name for field in self.model._meta.fields]
        valid_kwargs = {key: value for key,
                        value in kwargs.items() if key in model_field_names}
        activate_package_response_log = super(UserRoomPurchaseConfirmResponseLogManager, self).create(
            **valid_kwargs
        )
        return activate_package_response_log


class UserRoomPurchaseConfirmResponseLog(models.Model):
    user_transaction = models.OneToOneField(
        to=UserTransaction,
        on_delete=models.RESTRICT,
        related_name=_('room_purchase_res_user_transaction'),
        verbose_name=_('user transaction'),
        unique=True,
        blank=False,
        null=False,
        primary_key=True,
        help_text=_(
            'the user transaction from which the response was generated'
        ),
        error_messages={
            'null': _('user transaction must be provided'),
            'unique': _('user transaction instance must be unique')
        }
    )

    api_response = models.JSONField(
        verbose_name=_('activate package api response data'),
        null=True,
        blank=False,
        help_text=_("activate package api response data"),
        error_messages={
            'blank': _('activate package api response data must be provided')
        }
    )

    objects = UserRoomPurchaseConfirmResponseLogManager()
