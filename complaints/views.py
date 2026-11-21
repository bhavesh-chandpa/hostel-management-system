from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .forms import ComplaintForm, ComplaintResponseForm
from .models import Complaint


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
def student_complaints(request):
    if request.user.role != User.Role.STUDENT or request.user.student_id is None:
        raise PermissionDenied
    complaints = Complaint.objects.filter(student=request.user.student).order_by("-submitted_at")
    return render(request, "complaints/student_complaints.html", {"complaints": complaints})


@login_required
def submit_complaint(request):
    if request.user.role != User.Role.STUDENT or request.user.student_id is None:
        raise PermissionDenied
    form = ComplaintForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        complaint = form.save(commit=False)
        complaint.student = request.user.student
        complaint.save()
        messages.success(request, "Your complaint was submitted successfully.")
        return redirect("student_complaints")
    return render(request, "complaints/submit_complaint.html", {"form": form})


@staff_role_required(User.Role.RECTOR)
def rector_complaints(request):
    complaints = Complaint.objects.select_related("student", "resolved_by").order_by("status", "-submitted_at")
    return render(request, "complaints/rector_complaints.html", {"complaints": complaints})


@staff_role_required(User.Role.RECTOR)
def respond_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    form = ComplaintResponseForm(request.POST or None, instance=complaint)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked = get_object_or_404(Complaint.objects.select_for_update(), pk=complaint_id)
            if locked.status in (Complaint.ComplaintStatus.RESOLVED, Complaint.ComplaintStatus.REJECTED):
                messages.warning(request, "This complaint is already closed.")
            else:
                locked.status = form.cleaned_data["status"]
                locked.response = form.cleaned_data["response"]
                locked.resolved_by = request.user.staff
                locked.save(update_fields=["status", "response", "resolved_by"])
                messages.success(request, "Complaint response saved.")
        return redirect("rector_complaints")
    return render(request, "complaints/respond_complaint.html", {"complaint": complaint, "form": form})
