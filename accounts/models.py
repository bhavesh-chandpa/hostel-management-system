from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db.models import Q


# ==========================================
# 1. STAFF TABLE
# ==========================================

class Staff(models.Model):

    staff_id = models.AutoField(primary_key=True)

    full_name = models.CharField(max_length=50)

    email = models.EmailField(max_length=50, unique=True)

    phone_number = models.CharField(max_length=20)

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    employee_number = models.CharField(
        max_length=20,
        unique=True
    )

    joining_date = models.DateField()

    employment_status = models.BooleanField(default=True)

    class Meta:
        db_table = 'staff_table'

    def __str__(self):
        return self.full_name


# ==========================================
# 2. STUDENT TABLE
# ==========================================

class Student(models.Model):

    class StudentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACTIVE = 'Active', 'Active'
        REJECTED = 'Rejected', 'Rejected'
        WITHDRAWN = 'Withdrawn', 'Withdrawn'
        GRADUATED = 'Graduated', 'Graduated'
        LEFT = 'Left', 'Left'

    student_id = models.AutoField(primary_key=True)

    full_name = models.CharField(max_length=50)

    email = models.EmailField(max_length=50, unique=True)

    phone_number = models.CharField(
        max_length=20,
        unique=True
    )

    date_of_birth = models.DateField()

    roll_number = models.CharField(
        max_length=20,
        unique=True
    )

    degree = models.CharField(max_length=20)

    year_of_study = models.PositiveSmallIntegerField()

    guardian_contact = models.CharField(max_length=20)

    home_address = models.CharField(max_length=250)

    student_status = models.CharField(
        max_length=12,
        choices=StudentStatus.choices,
        default=StudentStatus.PENDING
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    reviewed_by = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='reviewed_by',
        related_name='reviewed_registrations'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    hostel_admission_date = models.DateField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'student_table'

    def __str__(self):
        return self.full_name


# ==========================================
# 3. LOGIN TABLE / CUSTOM DJANGO USER
# ==========================================


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):

        if not username:
            raise ValueError('Username is required.')

        student = extra_fields.get('student')
        staff = extra_fields.get('staff')
        role = extra_fields.get('role')

        # Exactly one profile must be linked.
        if (student is None) == (staff is None):
            raise ValueError(
                'A user must be linked to exactly one Student or Staff record.'
            )

        # Validate role and profile relationship.
        if student is not None and role != self.model.Role.STUDENT:
            raise ValueError('A Student profile must have the Student role.')

        if staff is not None and role not in (
            self.model.Role.ADMIN,
            self.model.Role.RECTOR,
            self.model.Role.ASSISTANT_RECTOR,
        ):
            raise ValueError('A Staff profile must have a staff role.')

        user = self.model(
            username=self.model.normalize_username(username),
            **extra_fields
        )

        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **extra_fields):

        staff = extra_fields.get('staff')

        if staff is None:
            raise ValueError('A superuser must be linked to a Staff record.')

        # Convert a Staff ID (integer or string) into a Staff object.
        if not isinstance(staff, Staff):
            try:
                staff = Staff.objects.get(pk=staff)
            except (Staff.DoesNotExist, ValueError, TypeError):
                raise ValueError('Please provide a valid Staff ID.')

        if extra_fields.get('student') is not None:
            raise ValueError(
                'A superuser cannot be linked to a Student record.'
            )

        extra_fields['staff'] = staff
        extra_fields['role'] = self.model.Role.ADMIN
        extra_fields['account_status'] = self.model.AccountStatus.ACTIVE
        extra_fields['is_superuser'] = True

        return self.create_user(
            username,
            password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN = 'Admin', 'Admin'
        RECTOR = 'Rector', 'Rector'
        ASSISTANT_RECTOR = 'Assistant Rector', 'Assistant Rector'
        STUDENT = 'Student', 'Student'

    class AccountStatus(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        INACTIVE = 'Inactive', 'Inactive'
        SUSPENDED = 'Suspended', 'Suspended'

    login_id = models.AutoField(primary_key=True)

    username = models.CharField(
        max_length=50,
        unique=True
    )

    # AbstractBaseUser provides password and last_login.
    # We extend the password column to match the dictionary.
    password = models.CharField(max_length=250)

    student = models.OneToOneField(
        Student,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='login_account'
    )

    staff = models.OneToOneField(
        Staff,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='login_account'
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    account_status = models.CharField(
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    # Createsuperuser will ask for the Staff ID.
    REQUIRED_FIELDS = ['staff']

    @property
    def is_active(self):
        return self.account_status == self.AccountStatus.ACTIVE

    @property
    def is_staff(self):
        return (
            self.role == self.Role.ADMIN
            and self.is_active
    )


    class Meta:
        db_table = 'login_table'

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(student__isnull=False, staff__isnull=True)
                    | Q(student__isnull=True, staff__isnull=False)
                ),
                name='login_exactly_one_profile'
            )
        ]


    def __str__(self):
        return f'{self.username} ({self.role})'