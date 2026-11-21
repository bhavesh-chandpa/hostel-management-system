from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .forms import NoticeForm
from .models import Notice

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

def active_notices(request):
    notices = Notice.objects.filter(is_active=True).select_related("posted_by").order_by("-posted_at")
    return render(request, "notices/active_notices.html", {"notices": notices})

@staff_role_required(User.Role.RECTOR, User.Role.ASSISTANT_RECTOR)
def manage_notices(request):
    form = NoticeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        notice = form.save(commit=False)
        notice.posted_by = request.user.staff
        notice.save()
        messages.success(request, "Notice published successfully.")
        return redirect("manage_notices")
    notices = Notice.objects.select_related("posted_by").order_by("-posted_at")
    return render(request, "notices/manage_notices.html", {"form": form, "notices": notices})

@staff_role_required(User.Role.RECTOR, User.Role.ASSISTANT_RECTOR)
@require_POST
def deactivate_notice(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    if notice.is_active:
        notice.is_active = False
        notice.save(update_fields=["is_active"])
        messages.success(request, "Notice deactivated. The record has been retained.")
    else:
        messages.info(request, "This notice is already inactive.")
    return redirect("manage_notices")
