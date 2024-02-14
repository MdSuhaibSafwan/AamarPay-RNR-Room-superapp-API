from django.contrib import admin

from .models import (
    PGPaymentRequestLog,
    PGPaymentResponseLog,
    PGPaymentVerificationResponseLog,
    UserTransaction
)


@admin.register(PGPaymentRequestLog)
class PGPaymentRequestLogAdmin(admin.ModelAdmin):
    list_display = [
        'pk'] + [
        field.name for field in PGPaymentRequestLog._meta.get_fields()
    ]


@admin.register(PGPaymentResponseLog)
class PGPaymentResponseLogAdmin(admin.ModelAdmin):
    list_display = [
        'pk'] + [
        field.name for field in PGPaymentResponseLog._meta.get_fields()
    ]


@admin.register(PGPaymentVerificationResponseLog)
class PGPaymentVerificationResponseLogAdmin(admin.ModelAdmin):
    list_display = [
        'pk'] + [
        field.name for field in PGPaymentVerificationResponseLog._meta.get_fields()
    ]


@admin.register(UserTransaction)
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'user_id', 'payment_verification_response', 'created_at'
    ]
