from django.contrib import admin
from .models import RNRAccessToken, RNRRoomReservation, RNRRoomReservationRefund


class RNRAccessTokenAdmin(admin.ModelAdmin):
    list_display = ["expired", "created", "expire_time"]


class RNRRoomReservationAdmin(admin.ModelAdmin):
    list_display = ["reservation_id", "property_id", "is_active"]


class RNRRoomReservationRefundAdmin(admin.ModelAdmin):
    list_display = ["reservation", "refunded", "date_created"]


admin.site.register(RNRAccessToken, RNRAccessTokenAdmin)
admin.site.register(RNRRoomReservation, RNRRoomReservationAdmin)
admin.site.register(RNRRoomReservationRefund, RNRRoomReservationRefundAdmin)
