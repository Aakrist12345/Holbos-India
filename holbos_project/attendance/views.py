import json
from datetime import date, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import StudentForm, TrainerLoginForm, TrainerSignupForm
from .models import AttendanceRecord, AttendanceSession, Student


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

def trainer_login(request):
    if request.user.is_authenticated:
        return redirect("attendance:dashboard")
    form = TrainerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.trainer)
        return redirect("attendance:dashboard")
    return render(request, "attendance/login.html", {"form": form})


def trainer_signup(request):
    if request.user.is_authenticated:
        return redirect("attendance:dashboard")
    form = TrainerSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        trainer = form.save()
        login(request, trainer)
        return redirect("attendance:dashboard")
    return render(request, "attendance/signup.html", {"form": form})


def trainer_logout(request):
    logout(request)
    return redirect("attendance:login")


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@login_required(login_url="attendance:login")
def dashboard(request):
    today = date.today()
    total_students = Student.objects.filter(is_active=True).count()

    today_records = AttendanceRecord.objects.filter(session__date=today)
    present_today = today_records.filter(status="Present").count()
    absent_today  = today_records.filter(status="Absent").count()
    total_sessions = AttendanceSession.objects.count()

    # Attendance % per class today
    classes_data = []
    for i in range(1, 11):
        cls = f"Class {i}"
        total = Student.objects.filter(student_class=cls, is_active=True).count()
        if total == 0:
            continue
        present = AttendanceRecord.objects.filter(
            session__date=today, session__student_class=cls, status="Present"
        ).count()
        classes_data.append({
            "class": cls,
            "total": total,
            "present": present,
            "pct": round(present / total * 100) if total else 0,
        })

    # Last 7 days overview
    week_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        rec = AttendanceRecord.objects.filter(session__date=d)
        week_data.append({
            "date": d.strftime("%d %b"),
            "present": rec.filter(status="Present").count(),
            "absent": rec.filter(status="Absent").count(),
        })

    context = {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "total_sessions": total_sessions,
        "classes_data": classes_data,
        "week_data_json": json.dumps(week_data),
        "today": today,
    }
    return render(request, "attendance/dashboard.html", context)


# ─────────────────────────────────────────────
# MARK ATTENDANCE
# ─────────────────────────────────────────────

@login_required(login_url="attendance:login")
def mark_attendance(request):
    return render(request, "attendance/mark.html")


@login_required(login_url="attendance:login")
def get_students_for_class(request):
    """AJAX: return students + existing attendance for a class+date."""
    cls  = request.GET.get("class", "")
    dt   = request.GET.get("date", "")
    if not cls or not dt:
        return JsonResponse({"error": "class and date are required"}, status=400)

    students = list(
        Student.objects.filter(student_class=cls, is_active=True)
        .order_by("name")
        .values("id", "name", "roll_number")
    )

    existing = {}
    try:
        session = AttendanceSession.objects.get(student_class=cls, date=dt)
        for rec in session.records.select_related("student"):
            existing[rec.student_id] = rec.status
    except AttendanceSession.DoesNotExist:
        pass

    return JsonResponse({"students": students, "existing": existing})


@login_required(login_url="attendance:login")
@require_POST
def submit_attendance(request):
    """AJAX: save a full attendance session."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    cls      = data.get("class", "").strip()
    dt       = data.get("date", "").strip()
    records  = data.get("records", {})   # {student_id: "Present"|"Absent"}

    if not cls or not dt or not records:
        return JsonResponse({"error": "class, date, and records are required"}, status=400)

    session, _ = AttendanceSession.objects.update_or_create(
        student_class=cls,
        date=dt,
        defaults={"trainer": request.user},
    )

    saved = 0
    for sid, status in records.items():
        student = get_object_or_404(Student, pk=int(sid))
        AttendanceRecord.objects.update_or_create(
            session=session, student=student,
            defaults={"status": status},
        )
        saved += 1

    return JsonResponse({"ok": True, "saved": saved, "session_id": session.id})


# ─────────────────────────────────────────────
# RECORDS
# ─────────────────────────────────────────────

@login_required(login_url="attendance:login")
def records(request):
    sessions = (
        AttendanceSession.objects
        .select_related("trainer")
        .prefetch_related("records__student")
        .order_by("-date")
    )
    cls_filter    = request.GET.get("class", "")
    status_filter = request.GET.get("status", "")
    date_from     = request.GET.get("from", "")
    date_to       = request.GET.get("to", "")

    if cls_filter:
        sessions = sessions.filter(student_class=cls_filter)
    if date_from:
        sessions = sessions.filter(date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__lte=date_to)

    # flatten to individual records for display
    flat = []
    for s in sessions:
        for r in s.records.all():
            if status_filter and r.status != status_filter:
                continue
            flat.append({
                "date": s.date.strftime("%d/%m/%Y"),
                "class": s.student_class,
                "student": r.student.name,
                "roll": r.student.roll_number,
                "status": r.status,
                "trainer": s.trainer.full_name or s.trainer.username,
            })

    context = {
        "records": flat,
        "total": len(flat),
        "cls_filter": cls_filter,
        "status_filter": status_filter,
        "date_from": date_from,
        "date_to": date_to,
        "classes": [f"Class {i}" for i in range(1, 11)],
    }
    return render(request, "attendance/records.html", context)


# ─────────────────────────────────────────────
# STUDENT MANAGEMENT
# ─────────────────────────────────────────────

@login_required(login_url="attendance:login")
def student_list(request):
    q   = request.GET.get("q", "").strip()
    cls = request.GET.get("class", "")
    students = Student.objects.filter(is_active=True).order_by("student_class", "name")
    if q:
        students = students.filter(name__icontains=q)
    if cls:
        students = students.filter(student_class=cls)
    context = {
        "students": students,
        "q": q,
        "cls_filter": cls,
        "classes": [f"Class {i}" for i in range(1, 11)],
        "total": students.count(),
    }
    return render(request, "attendance/students.html", context)


@login_required(login_url="attendance:login")
def add_student(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("attendance:students")
    return render(request, "attendance/add_student.html", {"form": form})


@login_required(login_url="attendance:login")
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.is_active = False
        student.save()
    return redirect("attendance:students")
