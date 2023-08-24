import uuid
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

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
        

