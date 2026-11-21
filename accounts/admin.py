from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.core.exceptions import ValidationError

from .models import Staff, Student, User


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("staff_id", "full_name", "employee_number", "email", "employment_status")
    list_filter = ("employment_status",)
    search_fields = ("full_name", "employee_number", "email", "phone_number")
    ordering = ("full_name",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "roll_number", "degree", "year_of_study", "student_status")
    list_filter = ("student_status", "degree", "year_of_study")
    search_fields = ("full_name", "roll_number", "email", "phone_number")
    readonly_fields = ("submitted_at", "reviewed_at")
    ordering = ("full_name",)


class HostelUserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ("username", "student", "staff", "role", "account_status")

    def clean(self):
        cleaned = super().clean()
        student, staff, role = cleaned.get("student"), cleaned.get("staff"), cleaned.get("role")
        if bool(student) == bool(staff):
            raise ValidationError("Select exactly one Student or Staff profile.")
        if student and role != User.Role.STUDENT:
            raise ValidationError("A Student profile must have the Student role.")
        if staff and role == User.Role.STUDENT:
            raise ValidationError("A Staff profile cannot have the Student role.")
        return cleaned


class HostelUserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = ("username", "password", "student", "staff", "role", "account_status", "is_superuser", "groups", "user_permissions")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = HostelUserCreationForm
    form = HostelUserChangeForm
    model = User
    list_display = ("username", "role", "account_status", "student", "staff", "is_active", "is_staff")
    list_filter = ("role", "account_status", "is_superuser")
    search_fields = ("username", "student__full_name", "staff__full_name")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Profile", {"fields": ("student", "staff", "role", "account_status")}),
        ("Permissions", {"fields": ("is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "student", "staff", "role", "account_status", "password1", "password2")}),
    )
    filter_horizontal = ("groups", "user_permissions")
