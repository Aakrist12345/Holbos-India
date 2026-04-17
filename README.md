# Holbos AttendERP — Setup Guide

Complete Django Attendance ERP system for Holbos. Trainers can log in,
mark attendance class-by-class, and view full records. Matches the
Holbos dark theme.

---

## Files Included

```
attendance/
├── __init__.py
├── apps.py
├── models.py          ← Trainer, Student, AttendanceSession, AttendanceRecord
├── views.py           ← All page + AJAX views
├── urls.py            ← URL routes (namespace: attendance)
├── forms.py           ← TrainerSignupForm, TrainerLoginForm, StudentForm
├── admin.py           ← Django admin registrations
└── management/
    └── commands/
        └── seed_students.py   ← python manage.py seed_students

templates/attendance/
├── base.html          ← Sidebar layout, topbar, nav, toast
├── login.html         ← Trainer sign-in
├── signup.html        ← Trainer registration
├── dashboard.html     ← Overview stats + charts
├── mark.html          ← Mark attendance (AJAX)
├── records.html       ← Filterable attendance history
├── students.html      ← Student list with search
└── add_student.html   ← Add new student

settings_additions.py     ← Settings snippets to merge
holbos_urls_snippet.py    ← URLs snippet to merge
```

---

## Step 1 — Copy files into your Holbos project

```
your_holbos_project/
├── holbos/              ← your main Django project folder
│   ├── settings.py
│   └── urls.py
├── attendance/          ← COPY THIS ENTIRE FOLDER HERE
└── templates/
    └── attendance/      ← COPY THIS ENTIRE FOLDER HERE
```

---

## Step 2 — Update settings.py

### A. Add app to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # existing apps...
    "attendance",
]
```

### B. Set AUTH_USER_MODEL

⚠️  This must be added BEFORE running your first migration.

```python
AUTH_USER_MODEL = "attendance.Trainer"
```

**If your project already has a custom user model** (e.g. a `Student`
model using AbstractUser), do NOT override AUTH_USER_MODEL. Instead,
add a ForeignKey in Trainer:

```python
# In attendance/models.py — replace AbstractBaseUser with:
from django.conf import settings

class Trainer(models.Model):
    user       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name  = models.CharField(max_length=200)
    # ... rest of fields
```

### C. Templates directory

Make sure TEMPLATES DIRS includes your project-level templates folder:

```python
TEMPLATES = [{
    ...
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    ...
}]
```

### D. Login redirects (optional)

```python
LOGIN_URL          = "/attendance/"
LOGIN_REDIRECT_URL = "/attendance/dashboard/"
```

---

## Step 3 — Update holbos/urls.py

```python
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("attendance/", include("attendance.urls", namespace="attendance")),
    # your existing routes...
]
```

---

## Step 4 — Run migrations

```bash
python manage.py makemigrations attendance
python manage.py migrate
```

---

## Step 5 — Seed sample students (optional)

```bash
python manage.py seed_students
```

This adds 25 pre-named students across Classes 1–5.

---

## Step 6 — Create a superuser / first trainer

```bash
python manage.py createsuperuser
```

Or use the Sign Up page at `/attendance/signup/`.

---

## Step 7 — Run and visit

```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000/attendance/

---

## URL Map

| URL                            | View                  |
|--------------------------------|-----------------------|
| /attendance/                   | Trainer login         |
| /attendance/signup/            | Trainer registration  |
| /attendance/logout/            | Log out               |
| /attendance/dashboard/         | Overview dashboard    |
| /attendance/mark/              | Mark attendance       |
| /attendance/records/           | Attendance records    |
| /attendance/students/          | Student list          |
| /attendance/students/add/      | Add student           |
| /attendance/students/<id>/delete/ | Remove student     |
| /attendance/api/students/      | AJAX: get class list  |
| /attendance/api/submit/        | AJAX: save attendance |

---

## Database Tables Created

| Model               | Table                          | Purpose                          |
|---------------------|-------------------------------|----------------------------------|
| Trainer             | attendance_trainer             | Trainer accounts (custom user)   |
| Student             | attendance_student             | Student records per class        |
| AttendanceSession   | attendance_attendancesession   | One per class per date           |
| AttendanceRecord    | attendance_attendancerecord    | One per student per session      |

---

## Features

- Trainer login / signup / logout
- Per-class, per-date attendance marking
- ✓ / ✕ toggle buttons — click again to undo
- Mark all present / mark all absent buttons
- Live present/absent counter as you mark
- AJAX submit — no page reload
- Filterable records by class, status, date range
- Student management (add, list, remove)
- Search students by name
- Weekly attendance bar chart on dashboard
- Per-class attendance % bars on dashboard
- Mobile responsive sidebar
- Matches Holbos dark theme (deep purple/magenta)

---

## Linking to Holbos Student Dashboard

To add an "Attendance" link in the existing Holbos student dashboard,
add this to the student-facing dashboard template:

```html
<a href="{% url 'attendance:dashboard' %}" class="btn btn-mag">
  View Attendance ERP →
</a>
```

Or in the spider web node, update the onclick for node4:

```javascript
// In dashboard.html spider JS, replace:
onclick="openPopup('attendance')"
// With:
onclick="window.location.href='/attendance/'"
```
