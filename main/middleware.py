from main.models import RNRAccessToken, RNRAnonymousUser


class RNRUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("RNR_AUTHORIZATION", None)
        if token is None:
            return self.set_anonymous_rnr_user(request)
        
        qs = RNRAccessToken.objects.filter(token=token)
        if not qs.exists():
            return self.set_anonymous_rnr_user(request)
        
        obj = qs.get()
        if obj.expired:
            return self.set_anonymous_rnr_user(request)
        
        self.set_rnr_user(request, obj)
        return self.get_response(request)
        
    def set_anonymous_rnr_user(self, request):
        setattr(request, "rnr_user", RNRAnonymousUser)
        return self.get_response(request)
    
    def set_rnr_user(self, request, rnr_access_token_obj):
        setattr(request, "rnr_user", rnr_access_token_obj.rnr_user)
