import json
from datetime import date, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import StudentForm, TrainerLoginForm, TrainerSignupForm, ParentCreateForm
from .models import AttendanceRecord, AttendanceSession, Student, Trainer

from django.contrib.admin.views.decorators import staff_member_required


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

def parent_login(request):
    if request.user.is_authenticated:
        return redirect("accounts:parentsdashboard")
    form = TrainerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.trainer)
        return redirect("accounts:parentsdashboard")
    return render(request, 'attendance/parent_login.html', {"form": form})


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
    """
    Refined dashboard: Optimized queries using aggregation to avoid DB loops.
    """
    today = date.today()
    
    # 1. Base Stats
    total_students = Student.objects.filter(is_active=True).count()
    today_sessions = AttendanceSession.objects.filter(date=today)
    
    # Pre-calculate counts for today using annotation
    today_records = AttendanceRecord.objects.filter(session__date=today)
    stats = today_records.aggregate(
        present=Count("id", filter=Q(status="Present")),
        absent=Count("id", filter=Q(status="Absent"))
    )
    present_today = stats["present"] or 0
    absent_today  = stats["absent"] or 0
    total_sessions = AttendanceSession.objects.count()

    # 2. Attendance % per class today (Optimized)
    # Get total students per class
    student_counts = (
        Student.objects.filter(is_active=True)
        .values("student_class")
        .annotate(total=Count("id"))
    )
    student_map = {item["student_class"]: item["total"] for item in student_counts}

    # Get present students per class
    present_counts = (
        AttendanceRecord.objects.filter(session__date=today, status="Present")
        .values("session__student_class")
        .annotate(present=Count("id"))
    )
    present_map = {item["session__student_class"]: item["present"] for item in present_counts}

    classes_data = []
    for cls_name, _ in Student.student_class.field.choices:
        total = student_map.get(cls_name, 0)
        if total == 0: continue
        
        present = present_map.get(cls_name, 0)
        classes_data.append({
            "class": cls_name,
            "total": total,
            "present": present,
            "pct": round((present / total * 100)) if total else 0
        })

    # 3. Last 7 days overview (Optimized)
    seven_days_ago = today - timedelta(days=6)
    history = (
        AttendanceRecord.objects.filter(session__date__gte=seven_days_ago)
        .values("session__date")
        .annotate(
            present=Count("id", filter=Q(status="Present")),
            absent=Count("id", filter=Q(status="Absent"))
        )
        .order_by("session__date")
    )
    
    # Ensure we show all 7 days even if no data exists
    history_map = {item["session__date"]: item for item in history}
    week_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        data = history_map.get(d, {"present": 0, "absent": 0})
        week_data.append({
            "date": d.strftime("%d %b"),
            "present": data["present"],
            "absent": data["absent"]
        })

    context = {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "total_sessions": total_sessions,
        "classes_data": classes_data,
        "week_data": week_data,
        "week_data_json": json.dumps(week_data),
        "today": today,
    }
    return render(request, "attendance/dashboard.html", context)

@staff_member_required(login_url='/admin/login/')
def erp_dashboard(request):
    return render(request, 'attendance/erp_dashboard.html')



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
    """
    Refined records view: Direct query on AttendanceRecord with optimized joins.
    """
    # 1. Filters
    cls_filter    = request.GET.get("class", "")
    status_filter = request.GET.get("status", "")
    date_from     = request.GET.get("from", "")
    date_to       = request.GET.get("to", "")

    # 2. Build Query
    queryset = AttendanceRecord.objects.select_related(
        "session", "session__trainer", "student"
    ).order_by("-session__date", "student__name")

    if cls_filter:
        queryset = queryset.filter(session__student_class=cls_filter)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if date_from:
        queryset = queryset.filter(session__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(session__date__lte=date_to)

    # 3. Context
    context = {
        "records": queryset,
        "total": queryset.count(),
        "cls_filter": cls_filter,
        "status_filter": status_filter,
        "date_from": date_from,
        "date_to": date_to,
        "classes": [c[0] for c in Student.student_class.field.choices],
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


# ─────────────────────────────────────────────
# PARENT MANAGEMENT
# ─────────────────────────────────────────────

@login_required(login_url="attendance:login")
def parents_list(request):
    # Only staff/trainers should probably see this
    parents = Trainer.objects.filter(is_staff=False).exclude(id=request.user.id).order_by("full_name")
    return render(request, "attendance/parents_list.html", {"parents": parents})


@login_required(login_url="attendance:login")
def create_parent(request):
    form = ParentCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("attendance:parents_list")
    return render(request, "attendance/create_parent.html", {"form": form})


@login_required(login_url="attendance:login")
def delete_parent(request, pk):
    parent = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        parent.is_active = False
        parent.save()
    return redirect("attendance:parents_list")
