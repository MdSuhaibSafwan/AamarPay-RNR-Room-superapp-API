from django.dispatch import receiver
from .models import RNRAccessToken
from django.db.models.signals import post_save
from django.db.models import Q


@receiver(signal=post_save, sender=RNRAccessToken)
def make_all_other_rnr_access_token_expired_other_than_this(sender, instance, created, **kwargs):
    if created:
        qs = RNRAccessToken.objects.filter(~Q(id=instance.id), expired=False)
        qs.update(expired=True)
