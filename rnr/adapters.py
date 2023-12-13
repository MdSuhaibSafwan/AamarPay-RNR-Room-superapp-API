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
    
    def get_authentication_token(self, access_token: RNRAccessToken=None, make_new=False):
        if make_new:
            obj = self.request_rnr_access_token()
            self.access_token = obj
            return self.access_token
        
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
        # print("Authentication headers", headers)
        # print("Authentication payload", payload)
        # print("Authentication url", url)

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
            self.get_authentication_token(make_new=True)
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
        data = {}
        data["offset"] = 0
        data["limit"] = 10
        query = ""
        query_seperator = "?"
        for i in data.keys():
            val = data[i]
            query += query_seperator
            query += f"{i}={val}"
            query_seperator = "&"

        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/search/destination/{destination}/{query}"
        data = self.request_a_url_and_get_data(url, method="get")
        if data.get("success") == True:
            counter = 0
            counter_lst = []
            data_lst = data.get("api_data").get("data")
            for each_data in data_lst:
                if each_data.get("destination_type") == "property":
                    print("Counting", counter)
                    counter_lst.append(counter)
                
                counter += 1   

            counter_lst.reverse()
            for i in counter_lst:
                try:
                    del data_lst[i]
                except Exception as e:
                    print(e)

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
        """
            STEP-1 --> BY PROPERTY ROOMS AVAILABILITY GET TOTAL PRICE
            STEP-2 --> USE PRICE CHECK API VIA SEARCH ID THAT GOT FROM STEP-1
            STEP-3 --> USE WALLET BALANCE CHECK API AND COMPARE TOTAL PRICE WITH BALANCE
            STEP-4 --> IF THERE IS ANY ISSUES GIVE A VALIDATION ERROR
            STEP-5 --> IF EVERYTHING IS FINE HOLD THE RESERVATION BY SENDING A REQUEST
            STEP-6 --> INSERT RESERVATION TO DB 
        """
        property_rooms_availability_data = {
            "check_in": payload.get("check_in"),
            "check_out": payload.get("check_out"),
            "property_id": payload.get("property_id"),
        }
        available_room_data = self.rnr_check_available_property_rooms(property_rooms_availability_data)
        if available_room_data.get("success") != True:
            resp_data = {
                "api_data": available_room_data["api_data"],
                "success": False,
                "error": True
            }
            return resp_data

        available_room_data = available_room_data["api_data"]["data"]
        available_room_list = available_room_data["rooms"]
        search_id = available_room_data["search_id"]
        rooms_to_book_list = payload.get("rooms")

        is_valid, data = self.validate_room_to_book_with_available_rooms(rooms_to_book_list, available_room_list)
        if not is_valid:
            resp_data = {
                "api_data": data,
                "message": "Invalid rooms to book",
                "success": False,
                "error": True
            }

        property_id = payload.get("property_id")
        price_check_payload = {
            "search_id": search_id,
            "property_id": property_id,
            "rooms": rooms_to_book_list
        }
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
        payload["search_id"] = search_id
        user = payload["user"]
        payload = self.get_payload_for_reservation_hold(payload)
        guest_name = payload.get("guest_name")
        guest_email = payload.get("guest_email")
        guest_mobile_no = payload.get("guest_mobile_no")
        guest_special_request = payload.get("guest_special_request")
        guest_address = payload.get("guest_address")
        data = self.request_a_url_and_get_data(url, method="post", data=json.dumps(payload))

        if data.get("success") == True:
            api_data = data.get("api_data")
            wallet_balance = float(self.get_wallet_balance())
            total_rate = float(data["api_data"]["data"]["grand_total_rate"])
            if wallet_balance < total_rate:
                error_msg = "We are having some trouble please retry after some time"
                return self.make_error({"error_note": error_msg})

            self.insert_reservation_to_db(api_data, property_id=property_id, user=user, 
                guest_name=guest_name, guest_email=guest_email, guest_mobile_no=guest_mobile_no, 
                guest_special_request=guest_special_request, guest_address=guest_address)

        return data

    def get_payload_for_reservation_hold(self, payload):
        del payload["check_in"]; del payload["check_out"]
        del payload["user"]
        payload["rooms_details"] = payload["rooms"]
        del payload["rooms"]
        return payload

    def is_balance_available(self, total_cost):
        wallet_balance = self.get_wallet_balance()
        return wallet_balance > total_cost

    def validate_room_to_book_with_available_rooms(self, rooms_to_book_list, available_room_list):
        if (len(rooms_to_book_list) > len(available_room_list)):
            return False, {"status": "Failed"}
        total_cost = 0
        for i_room in rooms_to_book_list:
            found_room = False
            for j_room in available_room_list:
                if i_room["id"] == j_room["id"]:
                    found_room = True
                    total_cost += self.find_total_cost_of_room(j_room['pricing']["guest"]["per_night"])
                    break

            if not found_room:
                return False, {"status": "Failed"}

        return True, {"status": "Success", "total": total_cost}

    def find_total_cost_of_room(self, data):
        net_rate = data.get("net_rate", None)
        vat = data.get("vat", None)
        service_charge = data.get("service_charge", None)
        return float(net_rate) + float(vat) + float(service_charge)

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

        if int(ap_status_code) != 2:
            return self.make_error(["Payment not successfull"])   
        
        pg_txid = data.get("pg_txid")
            
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/reservation/confirm/{reservation_id}/"
        data = self.request_a_url_and_get_data(url, method="patch")
        if data.get("success") == False:
            return self.make_error(data["api_data"])
        
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
            "guest_name": data.get("guest_name", kwargs.get("guest_name")),
            "guest_email": data.get("guest_email", kwargs.get("guest_email")),
            "guest_mobile_no": data.get("guest_mobile_no", kwargs.get("guest_mobile_no")),
            "guest_address": data.get("guest_address", kwargs.get("guest_address")),
            "guest_special_request": data.get("guest_special_request", kwargs.get("guest_special_request")),
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

    def cancel_reservation(self, data):
        reservation_id = data.get("reservation_id")
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/lodging/reservation/cancel/{reservation_id}/"
        data = self.request_a_url_and_get_data(url, "delete")
        if data.get("success") != True:
            return data

        try:
            reservation_obj = RNRRoomReservation.objects.get(reservation_id=reservation_id)
        except ObjectDoesNotExist:
            return data

        refund_obj, created = RNRRoomReservationRefund.objects.get_or_create(reservation=reservation_obj)
        return data
    
    def check_wallet_balance(self):
        url = f"{settings.RNR_BASE_URL}/api-b2b/v1/wallet/balance/"
        r = requests.get(url)
        data = r.json()
        return data

    def get_wallet_balance(self):
        data = self.check_wallet_balance()
        success = data.get("status") == "Succeed"
        if not success:
            return 0

        return data["data"]["balance"]


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

        url = f"{settings.AAMARPAY_DEV_URL}/api/v1/trxcheck/request.php{query}"
        r = requests.get(url, )
        return r.json()
    
    def verify_transaction(self, mer_txid, reservation_id):
        data = self.search_transaction(mer_txid)
        pg_status_code = data.get("status_code", None)
        if pg_status_code is None:
            return {"verified": False, "data": data, "error_msg": "invalid request id or store id"}

        if pg_status_code != 2:
            return {"verified": False, "data": data, "error_msg": "payment not successfull"}
        
        pg_meta_reservation_id = data.get("opt_c")
        if pg_meta_reservation_id is None:
            return {"verified": False, "data": data, "error_msg": "Reservation id not provided"}
        
        if reservation_id != pg_meta_reservation_id:
            return {"verified": False, "data": data, "error_msg": "Reservation id provided does not match the pg meta reservation id"}

        return {"verified": True, "data": data}


