import json
import requests
from .models import RNRAccessToken
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class RNRRoomsAdapter:

    def __init__(self):
        self.access_token = self.get_authentication_token()

    def get_authentication_url(self):   
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/identity/token/grant"
        return url
    
    def get_authentication_token(self, access_token: RNRAccessToken=None):
        if not access_token:
            qs = RNRAccessToken.objects.filter(expired=False)
            if not qs.exists():
                self.access_token = self.request_rnr_access_token()
                return self.access_token
            
            obj = qs.get()
            self.access_token = obj
            return obj
        
        if access_token.has_expired():
            self.access_token = self.request_rnr_access_token()
            return self.access_token

        self.access_token = access_token
        return self.access_token
    
    def request_rnr_access_token(self):
        headers = self.get_headers()
        payload = self.get_authentication_payload()
        url = self.get_authentication_url()
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            raise ValueError(r.text)
        
        data = r.json()["data"]
        token_obj = self.insert_access_token_to_db(data)
        self.access_token = token_obj
        return token_obj
    
    def insert_access_token_to_db(self, data):
        token = data.get("token")
        token_type = data.get("token_type")
        expire_time = data.get("expires_in") - 100
        try:
            obj = RNRAccessToken.objects.create(
                token=token, token_type=token_type, expire_time=expire_time
            )
        except IntegrityError as e:
            print(e)
            return None
        
        return obj

    def get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": settings.RNR_API_KEY,
            "x-api-secret": settings.RNR_API_SECRET_KEY
        }

        return headers
    
    def get_authentication_payload(self):
        payload = {
            "username": settings.RNR_USERNAME,
            "password": settings.RNR_PASSWORD
        }

        return payload
    
    def get_total_headers(self):
        headers = self.get_headers()
        authentication_token_obj = self.get_authentication_token(self.access_token)
        headers["Authorization"] = authentication_token_obj.token
        return headers

    def request_rnr_destination(self, destination):
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/destination/{destination}/"
        data = self.request_a_url_and_get_data(url, method="get")
        return data

    def request_a_url_and_get_data(self, url, method, **kwargs):
        headers = self.get_total_headers()
        r = getattr(requests, method)(url, headers=headers, **kwargs)
        if (r.status_code >= 200) and (r.status_code <= 204):
            return r.json()
        
        if r.status_code == 401:
            self.get_authentication_token()
            self.request_a_url_and_get_data(url, method, **kwargs)
        
        return self.error(r.json())
    
    def error(self, json_data):
        return json_data