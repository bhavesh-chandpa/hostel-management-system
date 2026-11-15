from django.urls import path
from . import views

urlpatterns = [
    path(
        '', 
        views.home, 
        name='home'
    ),
    path(
        'student-dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),
    path(
        'leave-application/',
        views.leave_application,
        name='leave_application'
    ),
    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),
]
