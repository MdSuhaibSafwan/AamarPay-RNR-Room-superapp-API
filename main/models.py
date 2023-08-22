import uuid
from django.db import models

def uuid_without_dash():
    return uuid.uuid4().hex


# class RNRRefreshToken(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid_without_dash)
#     token = models.CharField(max_length=300, unique=True)
#     expired = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"< Refresh-Token {self.token}>"


class RNRUser(models.Model):
    username = models.CharField(max_length=256)

    def __str__(self):
        return "<RNR User %s>" % self.username


class RNRAccessToken(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid_without_dash)
    # rnr_refresh_token = models.ForeignKey(RNRRefreshToken, on_delete=models.CASCADE)
    rnr_user = models.ForeignKey(RNRUser, on_delete=models.SET_NULL, null=True)
    token = models.CharField(max_length=300, unique=True)
    token_type = models.CharField(max_length=100, null=True)
    expired = models.BooleanField(default=False)
    expire_time = models.FloatField(default=3600.00)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"< Access-Token {self.token}>"

