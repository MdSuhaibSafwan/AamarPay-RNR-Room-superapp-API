from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("rnr/api/", include("rnr.api.urls")),
]
