from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def home(request):
    context = {
        'system_name': 'Hostel Management System',
        'student_name': 'Bhavesh',
        'total_rooms': 50,
    }
    return render(request, 'core/home.html')

@login_required
def student_dashboard(request):
    context = {
        'student_name': 'Rahul',
        'room_number': 205,
        'hostel_name': 'Xavier Hostel',
        'is_active': True,
        'subjects': [
            'Python',
            'DBMS',
            'Java',
            'Web Development'
        ]
    }
    return render(request, 'core/student_dashboard.html', context)

@login_required
def leave_application(request):

    if request.method == 'POST':

        form = LeaveApplicationForm(request.POST)

        if form.is_valid():

            student_name = form.cleaned_data['student_name']

            return render(
                request,
                'core/leave_application.html',
                {
                    'form': LeaveApplicationForm(),
                    'success': True,
                    'student_name': student_name
                }
            )

    else:
        form = LeaveApplicationForm()

    return render(
        request,
        'core/leave_application.html',
        {'form': form}
    )


def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('student_dashboard')

    else:

        form = RegisterForm()

    return render(
        request,
        'core/register.html',
        {'form': form}
    )


def login_view(request):

    if request.method == 'POST':

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect('student_dashboard')

    else:

        form = AuthenticationForm(request)

    return render(
        request,
        'core/login.html',
        {'form': form}
    )


@require_POST
def logout_view(request):

    logout(request)

    return redirect('home')