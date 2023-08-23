from django.urls import path
from . import views

urlpatterns = [
    path("authentication/", views.RNRUserAuthenticationAPIView.as_view(), ),
]
