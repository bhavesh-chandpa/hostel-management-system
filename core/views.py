from functools import wraps
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.forms import RegistrationDecisionForm, StudentRegistrationForm
from accounts.models import Student, User

def home(request):
    return render(request, "core/home.html", {"system_name": "Hostel Management System"})

def role_dashboard_redirect(user):
    if user.role == User.Role.ADMIN:
        return redirect("admin:index")
    if user.role == User.Role.RECTOR:
        return redirect("registration_requests")
    if user.role == User.Role.ASSISTANT_RECTOR:
        return redirect("manage_notices")
    if user.role == User.Role.STUDENT:
        return redirect("student_dashboard")
    raise PermissionDenied

@login_required
def student_dashboard(request):
    if request.user.role != User.Role.STUDENT or request.user.student_id is None:
        raise PermissionDenied
    student = request.user.student
    allocation = student.room_allocations.filter(is_current=True).select_related("room_number").first()
    return render(request, "core/student_dashboard.html", {"student": student, "current_allocation": allocation})

def register_view(request):
    if request.user.is_authenticated:
        return role_dashboard_redirect(request.user)
    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student = form.save()
        messages.success(request, "Your application has been received and is pending review.")
        return render(request, "core/registration_submitted.html", {"student": student})
    return render(request, "core/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return role_dashboard_redirect(request.user)
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return role_dashboard_redirect(user)
    return render(request, "core/login.html", {"form": form})

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")

def rector_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.RECTOR or request.user.staff_id is None:
            raise PermissionDenied
        if not request.user.staff.employment_status:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

@rector_required
def registration_requests(request):
    students = Student.objects.filter(student_status=Student.StudentStatus.PENDING).order_by("submitted_at")
    return render(request, "core/registration_requests.html", {"students": students})

@rector_required
def review_registration(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if student.student_status != Student.StudentStatus.PENDING:
        messages.warning(request, "This application has already been reviewed.")
        return redirect("registration_requests")
    form = RegistrationDecisionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            student = get_object_or_404(Student.objects.select_for_update(), pk=student_id)
            if student.student_status != Student.StudentStatus.PENDING:
                messages.warning(request, "This application has already been processed.")
                return redirect("registration_requests")
            student.reviewed_by = request.user.staff
            student.reviewed_at = timezone.now()
            student.remarks = form.cleaned_data["remarks"]
            if form.cleaned_data["decision"] == "approve":
                User.objects.create_user(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["temporary_password"],
                    student=student, role=User.Role.STUDENT,
                    account_status=User.AccountStatus.ACTIVE,
                )
                student.student_status = Student.StudentStatus.ACTIVE
                student.hostel_admission_date = timezone.localdate()
            else:
                student.student_status = Student.StudentStatus.REJECTED
            student.save()
        messages.success(request, f"Application for {student.full_name} was {student.student_status.lower()}.")
        return redirect("registration_requests")
    return render(request, "core/registration_review.html", {"student": student, "form": form})
