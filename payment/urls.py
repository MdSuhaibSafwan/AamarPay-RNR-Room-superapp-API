from django.urls import path
from .views import (
    PaymentInitiateGenericAPIView,
    PaymentSuccessGenericAPIView,
    PaymentFailureGenericAPIView,
    PaymentCancelGenericAPIView
)


urlpatterns = [
    path(
        'payment-initiate/',
        PaymentInitiateGenericAPIView.as_view(),
        name='payment-initiate'
    ),
    path(
        'payment-success/',
        PaymentSuccessGenericAPIView.as_view(),
        name='payment-success'
    ),
    path(
        'payment-failure/',
        PaymentFailureGenericAPIView.as_view(),
        name='payment-failure'
    ),
    path(
        'payment-cancelled/',
        PaymentCancelGenericAPIView.as_view(),
        name='payment-cancelled'
    ),
]
