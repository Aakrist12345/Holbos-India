import json
import logging
from datetime import date, timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import StudentForm, TrainerLoginForm, TrainerSignupForm, ParentCreateForm
from .models import AttendanceRecord, AttendanceSession, Student, Trainer, CLASS_CHOICES, CompensationBooking
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings

def trainer_login(request):
    if request.GET.get('autologin') == 'true' and request.GET.get('user'):
        username = request.GET.get('user')
        if request.user.is_authenticated and request.user.username == username:
            if getattr(request.user, 'is_parent', False):
                return redirect("accounts:dashboard")
            return redirect("attendance:dashboard")

    if request.user.is_authenticated:
        if getattr(request.user, 'is_parent', False):
            return redirect("accounts:dashboard")
        return redirect("attendance:dashboard")
    form = TrainerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.trainer
        if getattr(user, 'is_parent', False):
            from django.contrib import messages
            messages.error(request, "Parent accounts must use the Parent Login portal.")
            return render(request, "attendance/login.html", {"form": form})
        login(request, user)
        return redirect("attendance:dashboard")
    return render(request, "attendance/login.html", {"form": form})

def parent_login(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'is_parent', False):
            return redirect("accounts:dashboard")
        return redirect("attendance:dashboard")
    from accounts.forms import UserLoginForm
    form = UserLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from django.contrib.auth import authenticate
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if getattr(user, 'is_parent', False):
                login(request, user)
                return redirect("accounts:dashboard")
            else:
                from django.contrib import messages
                messages.error(request, "Access denied. Only parent accounts are allowed to log in through this portal.")
        else:
            from django.contrib import messages
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/parentslogin.html', {"form": form})

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
    return redirect("attendance:trainer_login")

@login_required(login_url="attendance:trainer_login")
def dashboard(request):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
    
    total_students = Student.objects.filter(is_active=True).count()
    today = date.today()
    #  Prepare attendance summary for dashboard
    today_records = AttendanceRecord.objects.filter(session__date=today)
    stats = today_records.aggregate(
        present=Count("id", filter=Q(status="Present")),
        absent=Count("id", filter=Q(status="Absent"))
    )
    present_today = stats["present"] or 0
    absent_today  = stats["absent"] or 0
    total_sessions = AttendanceSession.objects.count()

    student_counts = (
        Student.objects.filter(is_active=True)
        .values("student_class")
        .annotate(total=Count("id"))
    )
    student_map = {item["student_class"]: item["total"] for item in student_counts}

    present_counts = (
        AttendanceRecord.objects.filter(session__date=today, status="Present")
        .values("session__student_class")
        .annotate(present=Count("id"))
    )
    present_map = {item["session__student_class"]: item["present"] for item in present_counts}

    classes_data = []
    for cls_name, _ in CLASS_CHOICES:
        total = student_map.get(cls_name, 0)
        if total == 0: continue
        present = present_map.get(cls_name, 0)
        classes_data.append({
            "class": cls_name,
            "total": total,
            "present": present,
            "pct": round((present / total * 100)) if total else 0
        })

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

@login_required(login_url="attendance:trainer_login")
def mark_attendance(request):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
    return render(request, "attendance/mark.html")

@login_required(login_url="attendance:trainer_login")
def get_students_for_class(request):
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

@login_required(login_url="attendance:trainer_login")
@require_POST
def submit_attendance(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    cls      = data.get("class", "").strip()
    dt       = data.get("date", "").strip()
    records  = data.get("records", {})
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

@login_required(login_url="attendance:trainer_login")
@require_POST
def book_compensation_slot(request):
    try:
        data = json.loads(request.body)
        slot = data.get("slot")
        student_name = data.get("student_name", "").strip()

        if slot not in ["Saturday", "Sunday"]:
            return JsonResponse(
                {"ok": False, "error": "Invalid slot"},
                status=400
            )

        student = request.user.get_linked_students().filter(
            name__iexact=student_name
        ).first()

        if not student:
            return JsonResponse(
                {"ok": False, "error": "Student not found"},
                status=404
            )

        booking = CompensationBooking.objects.create(
            student=student,
            parent=request.user,
            slot_type=slot,
        )

        # Email notification to Holbos team
        subject = f"New Compensation Slot Booking - {slot}"

        message = f"""
New Compensation Slot Booking Received

Student Name: {student.name}

Parent Name: {request.user.full_name or request.user.username}

Parent Username: {request.user.username}

Parent Email: {request.user.email}

Slot Selected: {slot}

Booking ID: {booking.id}

Please contact the parent for confirmation.

Regards,
Holbos ERP
"""

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [
                    "holbosindia@gmail.com",
                    "aakholbos7497@gmail.com",
                ],
                fail_silently=False,
            )
            print("✅ Booking email sent successfully")

        except Exception as email_error:
            print("❌ Email sending failed:", email_error)

        return JsonResponse({
            "ok": True,
            "message": "✅ Slot booked successfully. Holbos team will contact you soon."
        })

    except Exception as e:
        print("Booking error:", e)
        return JsonResponse(
            {"ok": False, "error": str(e)},
            status=500
        )



@login_required(login_url="attendance:trainer_login")
def records(request):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")

    cls_filter    = request.GET.get("class", "")
    status_filter = request.GET.get("status", "")
    date_from     = request.GET.get("from", "")
    date_to       = request.GET.get("to", "")

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

    context = {
        "records": queryset,
        "total": queryset.count(),
        "cls_filter": cls_filter,
        "status_filter": status_filter,
        "date_from": date_from,
        "date_to": date_to,
        "classes": [c[0] for c in CLASS_CHOICES],
    }
    return render(request, "attendance/records.html", context)

@login_required(login_url="attendance:trainer_login")
def student_list(request):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
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

@login_required(login_url="attendance:trainer_login")
def add_student(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("attendance:students")
    return render(request, "attendance/add_student.html", {"form": form})

@login_required(login_url="attendance:trainer_login")
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.is_active = False
        student.save()
    return redirect("attendance:students")

@login_required(login_url="attendance:trainer_login")
def parents_list(request):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
    parents = Trainer.objects.filter(is_parent=True).order_by("full_name")
    return render(request, "attendance/parents_list.html", {"parents": parents})

@login_required(login_url="attendance:trainer_login")
def create_parent(request):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
        
    form = ParentCreateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            try:
                user = form.save()
                from django.contrib import messages
                messages.success(request, f"Parent account for {user.full_name or user.username} created successfully.")
                
                subject = 'Welcome to Holbos India - Parent Portal'
                email_body = f'Hi {user.full_name or user.username},\n\n' \
                             f'Your parent account has been successfully created on Holbos India AttendERP.\n' \
                             f'You can now log in to the Parent Portal to view your child\'s attendance and performance.\n\n' \
                             f'Login here: http://{request.get_host()}/parents-login/\n\n' \
                             f'Best regards,\nHolbos India Team'
                try:
                    if user.email:
                        send_mail(
                            subject,
                            email_body,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=True
                        )
                except Exception:
                    pass
                return redirect("attendance:create_parent")
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            from django.contrib import messages
            messages.error(request, "Please correct the errors below.")
            
    return render(request, "attendance/create_parent.html", {"form": form})

@login_required(login_url="attendance:trainer_login")
def delete_parent(request, pk):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
    parent = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        parent.is_active = not parent.is_active
        parent.save()
    return redirect("attendance:parents_list")

@login_required(login_url="attendance:trainer_login")
def hard_delete_parent(request, pk):
    if getattr(request.user, 'is_parent', False):
        return redirect("accounts:dashboard")
    parent = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        parent.delete()
    return redirect("attendance:parents_list")
