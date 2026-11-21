# Hostel Management System

A Django-based hostel administration portal for St. Xavier's Men's Hostel, Ahmedabad. The current portfolio MVP focuses on four prioritised workflows: room management and allocation, leave applications, complaint management and notices.

## Implemented workflows

### Student
- View profile and current room/bed allocation.
- Submit leave applications and track approval/rejection.
- Submit complaints and read staff responses.
- View active hostel notices.

### Rector
- Review pending hostel registration applications and approve/reject them.
- Add rooms, edit room capacity/status and mark unoccupied rooms under maintenance.
- Allocate beds to active students with occupancy and duplicate-allocation checks.
- Review and approve/reject leave applications.
- Review complaints, update their status and respond.
- Publish and deactivate notices.

### Assistant Rector
- Publish and deactivate notices.

### Admin
- Access the Django admin site using an Admin-role account.
- Manage student/staff profiles and login accounts through the custom admin configuration.

## Screenshots

The release ZIP includes screenshots captured from the running demo site by the GitHub Actions workflow. The captures include the public homepage, student dashboard, room management, leave workflows, complaints and notices.

## Technology stack

- Python 3.14
- Django 6.1
- MySQL 8.4 and MySQL Connector/Python
- HTML, page-specific CSS and JavaScript

The frontend uses one shared base stylesheet and separate stylesheets for the homepage, authentication, student dashboard, room management, leave, complaints and notices. The old single stylesheet is retained as a legacy file but is no longer loaded by the base template.

## Project structure

~~~text
accounts/             Custom User, Student and Staff models
rooms/                Room inventory and allocation
leave_management/     Student leave requests and Rector decisions
complaints/           Student complaints and Rector responses
notices/              Active notices and staff publishing/deactivation
attendance/           Attendance model and Django admin
fees/                 Fee models and Django admin
core/                 Public pages, login, registration review and dashboard
config/               Django settings and root URL configuration
screenshots/          UI captures generated for the release archive
~~~

## Setup (Windows PowerShell)

1. Install Python 3.14 and MySQL Server 8.4.
2. Open the project folder in PowerShell.
3. Create and activate a virtual environment:

~~~powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
~~~

4. Install dependencies:

~~~powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

5. Create a MySQL database and a dedicated application user. Run this SQL as a MySQL administrator and choose your own secure password:

~~~sql
CREATE DATABASE hostel_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hostel_app'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON hostel_management.* TO 'hostel_app'@'localhost';
FLUSH PRIVILEGES;
~~~

6. Copy the environment template and edit the database credentials:

~~~powershell
Copy-Item .env.example .env
~~~

Keep .env private. It is excluded by .gitignore.

7. Apply migrations, optionally create demonstration records, and start the development server:

~~~powershell
python manage.py check
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
~~~

8. Open http://127.0.0.1:8000/.

## Demonstration accounts

The seed_demo command creates the following accounts when they do not already exist:

| Role | Username | Password |
|---|---|---|
| Rector | demo.rector | DemoRector@123 |
| Assistant Rector | demo.assistant | DemoAssistant@123 |
| Student | demo.student | DemoStudent@123 |

The command also creates one active demo student, one pending applicant, room 101, a sample leave application, a sample complaint and a welcome notice. These credentials and records are for local demonstration only. Change or remove them before deployment.

## Admin account setup

First create a Staff profile in the Django shell, then create a superuser linked to that profile:

~~~powershell
python manage.py shell
~~~

~~~python
from django.utils import timezone
from accounts.models import Staff, User

admin_staff = Staff.objects.create(
    full_name="Hostel Administrator",
    email="admin@example.com",
    phone_number="9000000000",
    employee_number="ADMIN-001",
    joining_date=timezone.localdate(),
)
User.objects.create_superuser(
    username="hosteladmin",
    password="Use-A-Strong-Password",
    staff=admin_staff,
)
~~~

The Admin role can access /admin/. Rector and Assistant Rector accounts do not receive Django admin access by default.

## Automated checks

The repository includes a GitHub Actions workflow for Django system checks, migration consistency and tests. Local tests can be run using SQLite without touching the MySQL database by setting temporary PowerShell environment variables:

~~~powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = "test_hostel.sqlite3"
$env:SECRET_KEY = "local-test-secret"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
~~~

Remove the temporary overrides to return to MySQL:

~~~powershell
Remove-Item Env:DB_ENGINE
Remove-Item Env:DB_NAME
Remove-Item Env:SECRET_KEY
~~~

## Database design

The custom authentication model is accounts.User, mapped to login_table. Set AUTH_USER_MODEL before the initial migrations are applied to a fresh database. Do not retrofit it into a database that has already been migrated with Django's default user model.

The approved business table naming is retained: student_table, staff_table, login_table, room_table, room_allocation_table, attendance_table, leave_table, complaint_table, notice_table, fee_structure_table and payment_table.

Room-change request attributes are held on the existing room allocation entity; no additional business table is introduced.

## MVP boundaries

The selected MVP implements room management/allocation, leave management, complaint management and notices, together with student registration review and the student dashboard.

The following remain outside the selected MVP and should not be represented as completed: room-change request workflow, attendance entry, fee collection/payment gateway, downloadable receipts, email delivery and a complete granular permissions editor. The attendance and fee models/admin registrations are retained in the project.

Student registration is visitor-accessible. A Rector reviews applications; a login account is created only after approval. Notices are deactivated rather than permanently deleted.

This is an academic/portfolio project for local demonstration, not a production deployment. Review security settings, secret handling, backups, database permissions, HTTPS, logging and deployment configuration before public hosting.

## Repository

GitHub: https://github.com/bhavesh-chandpa/hostel-management-system
