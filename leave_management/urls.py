from django.urls import path
from . import views

urlpatterns = [
    path("student/leave/", views.student_leave_list, name="student_leave_list"),
    path("student/leave/apply/", views.apply_leave, name="apply_leave"),
    path("rector/leave/", views.rector_leave_list, name="rector_leave_list"),
    path("rector/leave/<int:leave_id>/decision/", views.decide_leave, name="decide_leave"),
]
