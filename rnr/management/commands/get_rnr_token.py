import json
import requests
from django.conf import settings
from django.core.management import BaseCommand
from ...models import RNRAccessToken
from django.db import IntegrityError


class Command(BaseCommand):

    def add_arguments(self, parser):
        return super().add_arguments(parser)
    
    def handle(self, *args, **options):
        self.stdout.write("Generating Token requesting RNR Rooms")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": settings.RNR_API_KEY,
            "x-api-secret": settings.RNR_API_SECRET_KEY
        }
        auth_payload = json.dumps({
            "username": settings.RNR_USERNAME,
            "password": settings.RNR_PASSWORD
        })
        r = requests.post(url=f"{settings.RNR_BASE_URL}/api-b2b/v1/identity/token/grant", headers=headers, data=auth_payload)
        if r.status_code != 200:
            self.stdout.write(self.style.ERROR("Requesting Failed at this moment try again later"))
            return None 

        data = r.json().get("data")
        token = data.get("token")
        self.stdout.write(self.style.SUCCESS(f"Token Generated \nToken: {token}"))

        token = data.get("token")
        token_type = data.get("token_type")
        expire_time = data.get("expires_in") - 100
        try:
            RNRAccessToken.objects.create(
                token=token, token_type=token_type, expire_time=expire_time
            )
        except IntegrityError as e:
            print(e)
            return None
        
