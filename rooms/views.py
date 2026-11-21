from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .forms import RoomAllocationForm, RoomForm
from .models import Room, RoomAllocation


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


@staff_role_required(User.Role.RECTOR)
def room_management(request):
    room_form = RoomForm(request.POST or None, prefix="room")
    allocation_form = RoomAllocationForm(request.POST or None, prefix="allocation")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_room" and room_form.is_valid():
            room_form.save()
            messages.success(request, "Room saved successfully.")
            return redirect("room_management")
        if action == "allocate_room" and allocation_form.is_valid():
            data = allocation_form.cleaned_data
            with transaction.atomic():
                room = Room.objects.select_for_update().get(pk=data["room_number"].pk)
                current = RoomAllocation.objects.select_for_update().filter(room_number=room, is_current=True)
                if current.count() >= room.capacity:
                    allocation_form.add_error("room_number", "The selected room has reached capacity.")
                elif current.filter(bed_number__iexact=data["bed_number"]).exists():
                    allocation_form.add_error("bed_number", "That bed is already occupied.")
                elif RoomAllocation.objects.filter(student=data["student"], is_current=True).exists():
                    allocation_form.add_error("student", "This student already has a current room.")
                else:
                    RoomAllocation.objects.create(
                        student=data["student"], room_number=room,
                        bed_number=data["bed_number"], decided_by=request.user.staff,
                        allocated_at=timezone.now(), is_current=True,
                    )
                    messages.success(request, f"Room {room.room_number} allocated to {data['student'].full_name}.")
                    return redirect("room_management")

    rooms = Room.objects.annotate(
        occupied=Count("allocations", filter=Q(allocations__is_current=True))
    ).order_by("room_number")
    allocations = RoomAllocation.objects.filter(is_current=True).select_related(
        "student", "room_number", "decided_by"
    ).order_by("room_number__room_number", "bed_number")
    return render(request, "rooms/room_management.html", {
        "room_form": room_form, "allocation_form": allocation_form,
        "rooms": rooms, "allocations": allocations,
    })


@staff_role_required(User.Role.RECTOR)
def toggle_room_status(request, room_number):
    if request.method != "POST":
        raise PermissionDenied
    room = get_object_or_404(Room, pk=room_number)
    if room.status and room.allocations.filter(is_current=True).exists():
        messages.error(request, "A room with current occupants cannot be placed under maintenance.")
    else:
        room.status = not room.status
        room.save(update_fields=["status"])
        label = "activated" if room.status else "marked under maintenance"
        messages.success(request, f"Room {room.room_number} {label}.")
    return redirect("room_management")
