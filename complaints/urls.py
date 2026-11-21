from django.urls import path
from . import views

urlpatterns = [
    path("student/complaints/", views.student_complaints, name="student_complaints"),
    path("student/complaints/new/", views.submit_complaint, name="submit_complaint"),
    path("rector/complaints/", views.rector_complaints, name="rector_complaints"),
    path("rector/complaints/<int:complaint_id>/", views.respond_complaint, name="respond_complaint"),
]
