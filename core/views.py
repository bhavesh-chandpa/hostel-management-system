from functools import wraps
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from accounts.forms import RegistrationDecisionForm
from accounts.models import Student, User
from django.shortcuts import render, redirect
from accounts.forms import StudentRegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def home(request):
    context = {
        'system_name': 'Hostel Management System',
    }
    return render(
        request,
        'core/home.html',
        context
    )


@login_required
def student_dashboard(request):

    # Only approved Student accounts can access this page.
    if (
        request.user.role != User.Role.STUDENT
        or request.user.student_id is None
    ):
        raise PermissionDenied

    student = request.user.student

    # Find the student's current room allocation.
    current_allocation = (
        student.room_allocations
        .filter(is_current=True)
        .select_related('room_number')
        .first()
    )

    context = {
        'student': student,
        'current_allocation': current_allocation,
    }

    return render(
        request,
        'core/student_dashboard.html',
        context
    )


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

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            student = form.save()

            return render(
                request,
                'core/registration_submitted.html',
                {'student': student}
            )

    else:
        form = StudentRegistrationForm()

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



# ==========================================
# RECTOR ACCESS CONTROL
# ==========================================

def rector_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if request.user.role != User.Role.RECTOR:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================
# VIEW PENDING REGISTRATION APPLICATIONS
# ==========================================

@login_required
@rector_required
def registration_requests(request):

    students = Student.objects.filter(
        student_status=Student.StudentStatus.PENDING
    ).order_by('submitted_at')

    return render(
        request,
        'core/registration_requests.html',
        {'students': students}
    )


# ==========================================
# REVIEW REGISTRATION APPLICATION
# ==========================================

@login_required
@rector_required
def review_registration(request, student_id):

    student = get_object_or_404(
        Student,
        student_id=student_id
    )

    if student.student_status != Student.StudentStatus.PENDING:
        return redirect('registration_requests')

    if request.method == 'POST':

        form = RegistrationDecisionForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                # Lock the application to prevent simultaneous processing.
                student = get_object_or_404(
                    Student.objects.select_for_update(),
                    student_id=student_id
                )

                if student.student_status != Student.StudentStatus.PENDING:
                    return redirect('registration_requests')

                decision = form.cleaned_data['decision']

                student.reviewed_by = request.user.staff
                student.reviewed_at = timezone.now()
                student.remarks = form.cleaned_data['remarks']

                if decision == 'approve':

                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['temporary_password'],
                        student=student,
                        role=User.Role.STUDENT,
                        account_status=User.AccountStatus.ACTIVE
                    )

                    student.student_status = Student.StudentStatus.ACTIVE
                    student.hostel_admission_date = timezone.localdate()

                else:

                    student.student_status = Student.StudentStatus.REJECTED

                student.save()

            return redirect('registration_requests')

    else:
        form = RegistrationDecisionForm()

    return render(
        request,
        'core/registration_review.html',
        {
            'student': student,
            'form': form
        }
    )
