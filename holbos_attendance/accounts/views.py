import calendar
import json
import random
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from attendance.models import AttendanceRecord, CompensationBooking, Student
from .forms import ParentSignupForm, UserLoginForm, UserSignupForm
from .models import PortfolioItem

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
        mobile_number = form.cleaned_data['mobile_number']
        user = User.objects.filter(mobile_number=mobile_number, is_parent=True).first()
        if user:
            if getattr(user, 'has_claimed_account', False):
                messages.error(request, "This parent account has already been claimed and secured with a custom password. You can no longer verify or claim it via the Parent Portal. Please log in directly or contact support if you forgot your password.")
                return render(request, 'accounts/parents_signup.html', {'form': form})
            # Generate random password
            raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.set_password(raw_password)
            user.has_claimed_account = True
            user.save()
            return render(request, 'accounts/parents_signup_success.html', {
                'unique_id': user.username,
                'password': raw_password
            })
        else:
            messages.error(request, "Mobile number not found in our records.")
            return render(request, 'accounts/parents_signup.html', {'form': form})
            
    return render(request, 'accounts/parents_signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'is_parent', False):
            return redirect('accounts:dashboard')
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
                return redirect('accounts:dashboard')
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
            return redirect('accounts:dashboard')
        if getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False):
            return redirect('attendance:dashboard')
        return redirect('accounts:dashboard')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if getattr(user, 'is_parent', False):
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Access denied. Only parent accounts are allowed to log in through this portal.")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/parentslogin.html', {'form': form})

@login_required(login_url='/parents-login/')
def parents_dashboard_view(request):
    if not getattr(request.user, 'is_parent', False) and not request.user.is_staff:
        return redirect('accounts:dashboard')
    
    children_filter = Q()
    if request.user.mobile_number:
        children_filter |= Q(parent_mobile__iexact=request.user.mobile_number)
    if request.user.email:
        children_filter |= Q(parent_email__iexact=request.user.email)
    children = Student.objects.filter(children_filter, is_active=True) if children_filter else Student.objects.none()
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


        c_bookings = [{
            'type': b.slot_type,
            'date': b.booking_date.strftime('%d %b %Y')
        } for b in CompensationBooking.objects.filter(student=child)]

        child_stats[str(child.id)] = {
            'present': c_present,
            'absent': c_absent,
            'total': c_total,
            'pct': c_pct,
            'attendance_map': c_map,
            'weekly_history': c_weekly,
            'absent_dates': c_absent_dates,
            'bookings': c_bookings,
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
            PortfolioItem.objects.create(
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

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            if getattr(user, 'is_parent', False):
                user.has_claimed_account = True
                user.save()
                return redirect('accounts:dashboard')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

def parents_forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        if not username or not mobile_number:
            messages.error(request, "Please enter both username and mobile number.")
        else:
            user = User.objects.filter(username=username, is_parent=True).first()
            if user and user.mobile_number == mobile_number:
                request.session['reset_password_user_id'] = user.id
                return redirect('accounts:parents_reset_password')
            else:
                messages.error(request, "No parent account matches the provided username and mobile number.")
    return render(request, 'accounts/parents_forgot_password.html')

def parents_reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    user_id = request.session.get('reset_password_user_id')
    if not user_id:
        messages.error(request, "Session expired or invalid access. Please start the process again.")
        return redirect('accounts:parents_forgot_password')
    user = User.objects.filter(id=user_id, is_parent=True).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect('accounts:parents_forgot_password')
    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if not password or not confirm_password:
            messages.error(request, "Please fill in all password fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        else:
            user.set_password(password)
            user.has_claimed_account = True
            user.save()
            del request.session['reset_password_user_id']
            messages.success(request, "Password reset successfully! You can now log in with your new password.")
            return redirect('accounts:parents_login')
    return render(request, 'accounts/parents_reset_password.html')
