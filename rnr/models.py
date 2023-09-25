import uuid
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

def uuid_without_dash():
    return uuid.uuid4().hex


class RNRAccessToken(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid_without_dash)
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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reservation_id = models.IntegerField()
    property_id = models.IntegerField()
    is_active = models.BooleanField(default=False)
    check_in = models.DateField()
    check_out = models.DateField()
    amount = models.FloatField()
    rnr_transaction_code = models.CharField(max_length=2040, null=True)
    pg_txid = models.CharField(max_length=2040, null=True)
    mer_txid = models.CharField(max_length=2040, null=True)
    currency = models.CharField(max_length=3)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reservation_id)


class RNRRoomReservationRefund(models.Model):
    reservation = models.OneToOneField(RNRRoomReservation, on_delete=models.CASCADE, )
    refunded = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reservation.reservation_id)

