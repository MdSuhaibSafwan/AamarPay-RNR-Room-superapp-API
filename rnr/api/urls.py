from django.urls import path
from . import views

urlpatterns = [
    path("search-destination/", views.RNRSearchDesinationAPIView.as_view(), ),
    path("property/search/", views.RNRPropertySearchAPIView.as_view(), ),
    path("property/search/<rnr_property_id>/", views.RNRGetPropertyProfileAPIView.as_view(), ),
    path("property/search/<rnr_property_id>/check-available-rooms/", views.RNRSearchPropertyAvailableRooms.as_view(), ),
    path("property/rooms/hold-reservation/", views.RNRReserveRoomHoldAPIView.as_view(), ),
    path("property/rooms/confirm-reservation/", views.RNRConfirmReservationAPIView.as_view(), ),
]
