from django.urls import path
from . import views

urlpatterns = [
    path("notices/", views.active_notices, name="active_notices"),
    path("staff/notices/", views.manage_notices, name="manage_notices"),
    path("staff/notices/<int:notice_id>/deactivate/", views.deactivate_notice, name="deactivate_notice"),
]
