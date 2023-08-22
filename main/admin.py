from django.contrib import admin
from .models import RNRUser, RNRAccessToken

admin.site.register(RNRUser)
admin.site.register(RNRAccessToken)
