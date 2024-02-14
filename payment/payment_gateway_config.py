from django.conf import settings

PAYMENT_GATEWAY_URL = "https://sandbox.aamarpay.com/jsonpost.php"
PAYMENT_VERIFICATOION_URL = "https://sandbox.aamarpay.com/api/v1/trxcheck/request.php"

PAYLOAD = {
    "store_id": "aamarpaytest",
    "currency": "BDT",
    "signature_key": "dbb74894e82415a2f7ff0ec3a97e4183",
    "type": "json"
}
