from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
import re


class PaymentInitiateSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    reservation_id = serializers.CharField()
    cus_name = serializers.CharField()
    cus_email = serializers.EmailField()
    cus_phone = serializers.CharField()
    desc = serializers.CharField()

    def validate_amount(self, amount):
        if amount < 0:
            raise serializers.ValidationError(
                detail=_("Amount cannot be negative."),
                code='invalid'
            )
        return amount

    def validate_cus_phone(self, phone_number):
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise serializers.ValidationError(
                detail=_('This phone number is not valid.'),
                code='invalid',
            )
        return phone_number
