from django.contrib import admin
from .models import RNRAccessToken


class RNRAccessTokenAdmin(admin.ModelAdmin):
    list_display = ["expired", "created", "expire_time"]


admin.site.register(RNRAccessToken, RNRAccessTokenAdmin)
