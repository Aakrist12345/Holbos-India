import calendar
from django.utils import timezone
import json
from attendance.models import Student, AttendanceRecord
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserSignupForm, UserLoginForm, ParentSignupForm
from .models import PortfolioItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = UserSignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('accounts:dashboard')
    return render(request, 'accounts/signup.html', {'form': form})

def parents_signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = ParentSignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        subject = 'Welcome to Holbos India - Parent Portal'
        email_body = f'Hi {user.full_name or user.username},\n\n' \
                     f'Your parent account has been successfully created on Holbos India AttendERP.\n' \
                     f'You can now log in to the Parent Portal to view your child\'s attendance and performance.\n\n' \
                     f'Login here: http://{request.get_host()}/parents-login/\n\n' \
                     f'Best regards,\nHolbos India Team'
        try:
            send_mail(
                subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True
            )
        except Exception:
            pass
        messages.success(request, "Thanks for creating an account at Holbos")
        return redirect('accounts:parents_login')
    return render(request, 'accounts/parents_signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'is_parent', False):
            return redirect('accounts:parentsdashboard')
        if getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False):
            return redirect('attendance:dashboard')
        return redirect('accounts:dashboard')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if getattr(user, 'is_parent', False):
                return redirect('accounts:parentsdashboard')
            if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
                return redirect('attendance:dashboard')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def dashboard_view(request):
    if getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False):
        return redirect('attendance:dashboard')
    if getattr(request.user, 'is_parent', False):
        return redirect('accounts:parentsdashboard')
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    is_parent = getattr(request.user, 'is_parent', False)
    logout(request)
    if is_parent:
        return redirect('accounts:parents_login')
    return redirect('accounts:login')

def parents_login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'is_parent', False):
            return redirect('accounts:parentsdashboard')
        if getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False):
            return redirect('attendance:dashboard')
        return redirect('accounts:parentsdashboard')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if getattr(user, 'is_parent', False):
                return redirect('accounts:parentsdashboard')
            if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
                return redirect('attendance:dashboard')
            return redirect('accounts:parentsdashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/parentslogin.html', {'form': form})

@login_required(login_url='/parents-login/')
def parents_dashboard_view(request):
    if not getattr(request.user, 'is_parent', False) and not request.user.is_staff:
        return redirect('accounts:dashboard')
    
    children = Student.objects.filter(parent_email__iexact=request.user.email, is_active=True)
    now = timezone.now()
    _, total_days_in_month = calendar.monthrange(now.year, now.month)
    first_day_of_month = calendar.weekday(now.year, now.month, 1) 

    records = AttendanceRecord.objects.filter(
        student__in=children
    ).select_related('session', 'student').order_by('-session__date')
    
    child_stats = {}
    for child in children:
        child_records = records.filter(student=child)
        c_present = child_records.filter(status="Present").count()
        c_absent = child_records.filter(status="Absent").count()
        c_total = c_present + c_absent
        c_pct = round((c_present / c_total) * 100) if c_total > 0 else 0
        c_map = {str(r.session.date.day): (1 if r.status == "Present" else 0) for r in child_records if r.session.date.month == now.month}
        
        c_weekly = []
        for r in child_records[:5]:
            c_weekly.append({
                'day': r.session.date.strftime('%a'),
                'ok': 1 if r.status == 'Present' else 0
            })
        c_weekly.reverse()
        c_absent_dates = [r.session.date.strftime('%d %b') for r in child_records if r.status == 'Absent']

        child_stats[str(child.id)] = {
            'present': c_present,
            'absent': c_absent,
            'total': c_total,
            'pct': c_pct,
            'attendance_map': c_map,
            'weekly_history': c_weekly,
            'absent_dates': c_absent_dates,
            'name': child.name
        }

    total_present = records.filter(status='Present').count()
    total_absent = records.filter(status='Absent').count()
    total_days = total_present + total_absent
    attendance_percentage = round((total_present / total_days) * 100) if total_days > 0 else 0

    context = {
        'children': children,
        'records': records,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_days': total_days,
        'attendance_percentage': attendance_percentage,
        'child_stats_json': json.dumps(child_stats),
        'first_day': first_day_of_month,
        'total_days_month': total_days_in_month,
    }
    return render(request, 'accounts/parentsdashboard.html', context)

@csrf_exempt
@login_required
def upload_portfolio(request):
    if request.method == 'POST':
        item_type = request.POST.get('type')
        title = request.POST.get('title', 'Untitled')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')

        if not file and item_type != 'Article':
            return JsonResponse({'success': False, 'message': 'No file uploaded'})

        try:
            item = PortfolioItem.objects.create(
                user=request.user,
                item_type=item_type,
                title=title,
                description=description,
                file=file
            )
            return JsonResponse({'success': True, 'message': 'Portfolio item uploaded successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
