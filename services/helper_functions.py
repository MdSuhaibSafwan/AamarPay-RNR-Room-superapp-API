from requests import Request, Session
from requests.adapters import HTTPAdapter, Retry


class RequestMixin:
    @staticmethod
    def make_request(*args, **kwargs):
        with Session() as s:
            payload_type = kwargs.get('payload_type', 'json')
            retries = Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[502, 503, 504]
            )
            s.mount('http://', HTTPAdapter(max_retries=retries))
            payload_args = {
                'method': kwargs.get('req_type').value,
                'url': kwargs.get('url'),
                payload_type: kwargs.get('payload'),
                'headers': kwargs.get('headers', {}),
                'params': kwargs.get('params', {})
            }
            req = Request(**payload_args)
            prepped = req.prepare()
            res = s.send(
                prepped,
                stream=False,
                verify=True,
                timeout=10
            )
            return res
