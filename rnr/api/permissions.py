from rest_framework.permissions import SAFE_METHODS, BasePermission


class RNRRoomComparePermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if request.method not in ["GET", "POST"]:
            return False

        return True
