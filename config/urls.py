from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("rooms.urls")),
    path("", include("leave_management.urls")),
    path("", include("complaints.urls")),
    path("", include("notices.urls")),
]
