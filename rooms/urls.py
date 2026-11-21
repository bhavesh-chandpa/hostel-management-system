from django.urls import path
from . import views

urlpatterns = [
    path("rector/rooms/", views.room_management, name="room_management"),
    path("rector/rooms/<int:room_number>/edit/", views.room_management, name="edit_room"),
    path("rector/rooms/<int:room_number>/status/", views.toggle_room_status, name="toggle_room_status"),
]
