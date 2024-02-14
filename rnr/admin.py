from django.contrib import admin
from .models import (
    RNRAccessToken,
    RNRRoomReservation,
    RNRRoomReservationRefund,
    UserRoomPurchaseHistory,
    UserRoomPurchaseConfirmResponseLog
)


@admin.register(UserRoomPurchaseHistory)
class UserRoomPurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'pk'] + [
        field.name for field in UserRoomPurchaseHistory._meta.get_fields()
    ]


@admin.register(UserRoomPurchaseConfirmResponseLog)
class UserRoomPurchaseConfirmResponseLogAdmin(admin.ModelAdmin):
    list_display = [
        'pk'] + [
        field.name for field in UserRoomPurchaseConfirmResponseLog._meta.get_fields()
    ]


class RNRAccessTokenAdmin(admin.ModelAdmin):
    list_display = ["expired", "created", "expire_time"]


class RNRRoomReservationAdmin(admin.ModelAdmin):
    list_display = ["reservation_id", "property_id", "is_active"]


class RNRRoomReservationRefundAdmin(admin.ModelAdmin):
    list_display = ["reservation", "refunded", "date_created"]


admin.site.register(RNRAccessToken, RNRAccessTokenAdmin)
admin.site.register(RNRRoomReservation, RNRRoomReservationAdmin)
admin.site.register(RNRRoomReservationRefund, RNRRoomReservationRefundAdmin)
