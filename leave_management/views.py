from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .forms import LeaveApplicationForm
from .models import LeaveApplication

def staff_role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles or request.user.staff_id is None:
                raise PermissionDenied
            if not request.user.staff.employment_status:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def student_leave_list(request):
    if request.user.role != User.Role.STUDENT or request.user.student_id is None:
        raise PermissionDenied
    applications = LeaveApplication.objects.filter(student=request.user.student).order_by("-applied_at")
    return render(request, "leave_management/student_leave_list.html", {"applications": applications})

@login_required
def apply_leave(request):
    if request.user.role != User.Role.STUDENT or request.user.student_id is None:
        raise PermissionDenied
    form = LeaveApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        leave = form.save(commit=False)
        leave.student = request.user.student
        leave.save()
        messages.success(request, "Your leave application was submitted.")
        return redirect("student_leave_list")
    return render(request, "leave_management/apply_leave.html", {"form": form})

@staff_role_required(User.Role.RECTOR)
def rector_leave_list(request):
    applications = LeaveApplication.objects.select_related("student", "processed_by").order_by("status", "-applied_at")
    return render(request, "leave_management/rector_leave_list.html", {"applications": applications})

@staff_role_required(User.Role.RECTOR)
def decide_leave(request, leave_id):
    if request.method != "POST":
        raise PermissionDenied
    decision = request.POST.get("decision")
    if decision not in (LeaveApplication.LeaveStatus.APPROVED, LeaveApplication.LeaveStatus.REJECTED):
        raise PermissionDenied
    with transaction.atomic():
        leave = get_object_or_404(LeaveApplication.objects.select_for_update(), pk=leave_id)
        if leave.status != LeaveApplication.LeaveStatus.PENDING:
            messages.warning(request, "This application has already been processed.")
        else:
            leave.status = decision
            leave.processed_by = request.user.staff
            leave.save(update_fields=["status", "processed_by"])
            messages.success(request, f"Leave application #{leave.leave_id} was {decision.lower()}.")
    return redirect("rector_leave_list")
