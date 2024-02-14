import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    if not re.match(r'^\+?1?\d{9,15}$', value):
        raise ValidationError(
            message=_('The phone number is not valid.'),
            code='invalid',
            params={
                'value': value
            }
        )
