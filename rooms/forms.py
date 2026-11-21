from django import forms
from accounts.models import Student
from .models import Room, RoomAllocation


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("room_number", "capacity", "status")
        widgets = {
            "room_number": forms.NumberInput(attrs={"min": 1, "class": "form-control"}),
            "capacity": forms.NumberInput(attrs={"min": 1, "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_room_number(self):
        number = self.cleaned_data["room_number"]
        qs = Room.objects.filter(room_number=number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A room with this number already exists.")
        return number

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity < 1:
            raise forms.ValidationError("Room capacity must be at least one.")
        if self.instance.pk:
            occupied = self.instance.allocations.filter(is_current=True).count()
            if capacity < occupied:
                raise forms.ValidationError(
                    f"Capacity cannot be lower than current occupancy ({occupied})."
                )
        return capacity


class RoomAllocationForm(forms.ModelForm):
    class Meta:
        model = RoomAllocation
        fields = ("student", "room_number", "bed_number")
        widgets = {
            "student": forms.Select(attrs={"class": "form-control"}),
            "room_number": forms.Select(attrs={"class": "form-control"}),
            "bed_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Bed 1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.filter(
            student_status=Student.StudentStatus.ACTIVE
        ).order_by("full_name")
        self.fields["room_number"].queryset = Room.objects.filter(
            status=True
        ).order_by("room_number")

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get("student")
        room = cleaned.get("room_number")
        bed = (cleaned.get("bed_number") or "").strip()
        if student and RoomAllocation.objects.filter(student=student, is_current=True).exists():
            self.add_error("student", "This student already has a current room allocation.")
        if room and bed:
            current = RoomAllocation.objects.filter(room_number=room, is_current=True)
            if current.count() >= room.capacity:
                self.add_error("room_number", "This room is already at full capacity.")
            if current.filter(bed_number__iexact=bed).exists():
                self.add_error("bed_number", "This bed is already occupied.")
        cleaned["bed_number"] = bed
        return cleaned
