import json
import requests
from .models import RNRAccessToken, RNRRoomReservation, RNRRoomReservationRefund
from django.conf import settings
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
            if obj.has_expired():
                obj = self.request_rnr_access_token()
                
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

    def request_a_url_and_get_data(self, url, method, **kwargs):
        headers = self.get_total_headers()
        r = getattr(requests, method)(url, headers=headers, **kwargs)
        if (r.status_code >= 200) and (r.status_code <= 204):
            return {
                "success": True,
                "error": False,
                "api_data": r.json()
            }
        
        if r.status_code == 401:
            print("Un authorized")
            self.get_authentication_token()
            return self.request_a_url_and_get_data(url, method, **kwargs)
        
        return self.make_error(r.json())
    
    def make_error(self, json_data):
        data = {
            "success": False,
            "error": True,
            "api_data": json_data
        }
        return data
    
    def rnr_check_available_property_rooms(self, data):
        query = ""
        query_seperator = "?"
        for i in data.keys():
            val = data[i]
            query += query_seperator
            query += f"{i}={val}"
            query_seperator = "&"
        
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/property/rooms/{query}"
        data = self.request_a_url_and_get_data(url, method="get")
        return data

    def rnr_search_destination(self, destination):
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/destination/{destination}/"
        data = self.request_a_url_and_get_data(url, method="get")
        return data
    
    def rnr_get_property_profile(self, property_id):
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/property-profile/{property_id}/"
        data = self.request_a_url_and_get_data(url, "get")
        return data

    def rnr_search_properties(self, data: dict):
        data["offset"] = 0
        data["limit"] = 10
        query = ""
        query_seperator = "?"
        for i in data.keys():
            val = data[i]
            query += query_seperator
            query += f"{i}={val}"
            query_seperator = "&"
        
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/properties{query}"
        data = self.request_a_url_and_get_data(url, method="get")
        return data

    def rnr_price_check(self, payload):
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/property/rooms/rate-check/"
        # print("price payload ", payload)
        data = self.request_a_url_and_get_data(url, method="post", data=json.dumps(payload))
        # print("Resp data ", data)
        return data

    def rnr_validate_price_check(self, payload):
        data = self.rnr_price_check(payload)
        return data.get("success", False)

    def rnr_reserve_rooms(self, payload: dict):
        property_id = payload.get("property_id")
        user = payload.pop("user")
        price_check_payload = {
            "search_id": payload.get("search_id"),
            "property_id": property_id,
            "rooms": payload.get("rooms_details")
        }
        # print("payload ", price_check_payload)
        is_valid = self.rnr_validate_price_check(price_check_payload)
        if not is_valid:
            resp_data = {
                "api_data": { 
                    "validation": "Failed",
                    "rooms": "not available",
                    "message": "room not available",
                },
                "success": False,
                "error": True
            }
            return resp_data
        
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/reservation/hold/"
        data = self.request_a_url_and_get_data(url, method="post", data=json.dumps(payload))
        if data.get("success") == True:
            api_data = data.get("api_data")
            self.insert_reservation_to_db(api_data, property_id=property_id, user=user)

        return data
    
    def rnr_confirm_reservation(self, reservation_id, mer_txid=None):
        if mer_txid is None:
            return self.make_error(["provide merchant transaction id"])
        
        query = ""
        query_seperator = "?"
        data = {
            "store_id": settings.AAMARPAY_STORE_ID,
            "signature_key": settings.AAMARPAY_SIGNATURE_KEY,
            "type": "json",
            "request_id": mer_txid
        }
        for i in data.keys():
            val = data[i]
            query += query_seperator
            query += f"{i}={val}"
            query_seperator = "&"

        url = f"{settings.AAMARPAY_DEV_URL}/api/v1/trxcheck/request.php{query}"
        r = requests.get(url)
        data = r.json()
        ap_status_code = data.get("status_code", None)
        if ap_status_code is None:
            return self.make_error(["Invalid merchant transaction id provided"])
        if ap_status_code != 2:
            return self.make_error(["Payment not successfull"])   
        
        pg_txid = data.get("pg_txid")
            
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/reservation/confirm/{reservation_id}/"
        data = self.request_a_url_and_get_data(url, method="patch")
        transaction_code = data.get("api_data").get("data")["payment"]["transaction_code"]
        self.confirm_reservation_in_db(reservation_id=reservation_id, transaction_code=transaction_code, 
                                       mer_txid=mer_txid, pg_txid=pg_txid)
        return data
    
    def insert_reservation_to_db(self, data: dict, **kwargs):
        data = data.get("data")
        reservation_hold_data = {
            "reservation_id": data.get("id"),
            "check_in": data.get("check_in"),
            "check_out": data.get("check_out"),
            "amount": data.get("grand_total_rate"),
            "currency": data.get("currency"),
            "property_id": data.get("property_id", kwargs.get("property_id", None)),
            "user": data.get("user", kwargs.get("user", None)),
            "currency": data.get("currency"),
        }

        obj = RNRRoomReservation.objects.create(**reservation_hold_data)    
        return obj
    
    def confirm_reservation_in_db(self, data: dict={}, **kwargs):
        reservation_id = data.get("reservation_id", kwargs.get("reservation_id", None))
        transaction_code = data.get("transaction_code", kwargs.get("transaction_code", None))
        pg_txid = data.get("pg_txid", kwargs.get("pg_txid", None))
        mer_txid = data.get("mer_txid", kwargs.get("mer_txid", None))
    
        try:
            obj = RNRRoomReservation.objects.get(reservation_id=reservation_id)
        except ObjectDoesNotExist:
            return None
        
        obj.is_active = True
        obj.rnr_transaction_code = transaction_code
        obj.pg_txid = pg_txid
        obj.mer_txid = mer_txid
        obj.save()
        return obj
    
    def ask_for_refund(self, data: dict):
        reservation_id = data.get("reservation_id", None)
        try:
            reservation_obj = RNRRoomReservation.objects.get(reservation_id=reservation_id)
        except ObjectDoesNotExist:
            return self.make_error("Reservation id not found")
        res_ref_obj, created = RNRRoomReservationRefund.objects.get_or_create(reservation=reservation_obj)
        return {
                "success": False,
                "error": True,
                "message": "Reservation added for refund",
                "reservation_refund_id": res_ref_obj.id,
                "reservation_id": reservation_obj.reservation_id
        }


class AamarpayPgAdapter:

    def __init__(self):
        self.store_id = settings.AAMARPAY_STORE_ID
        self.signature_key = settings.AAMARPAY_SIGNATURE_KEY
        self.dev_url = settings.AAMARPAY_DEV_URL

    def search_transaction(self, mer_txid):
        url_params = {
            "request_id": mer_txid,
            "store_id": self.store_id,
            "signature_key": self.signature_key,
            "type": "json"
        }
        query = ""
        query_seperator = "?"
        
        for i in url_params.keys():
            val = url_params[i]
            query += query_seperator
            query += f"{i}={val}"
            query_seperator = "&"

        url = f"http://sandbox.aamarpay.com/api/v1/trxcheck/request.php{query}"
        r = requests.get(url, )
        return r.json()
    
    def verify_transaction(self, mer_txid, reservation_id):
        data = self.search_transaction(mer_txid)
        pg_status_code = data.get("status_code", None)
        if pg_status_code is None:
            return {"verified": False, "data": data, "status": "invalid request id or store id"}

        if pg_status_code != 2:
            return {"verified": False, "data": data, "status": "payment not successfull"}
        
        opt_a = json.laods(data.get("opt_a"))
        pg_meta_reservation_id = opt_a.get("reservation_id", None)
        if pg_meta_reservation_id is None:
            return {"verified": False, "data": data, "status": "Reservation id not provided"}
        
        if reservation_id != pg_meta_reservation_id:
            return {"verified": False, "data": data, "status": "Reservation id provided does not match the pg meta reservation id"}

        return {"verified": True, "data": data}


