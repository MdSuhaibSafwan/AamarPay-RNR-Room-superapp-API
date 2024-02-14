from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/rnr/", include("rnr.api.urls")),
    path('payment/', include('payment.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(), name='swagger'),
    path('schema/redoc/', SpectacularRedocView.as_view(), name='redoc'),
]
