from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserSignupForm, UserLoginForm

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

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def attendance_view(request):
    return render(request, 'accounts/attendance.html')

def parents_login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:parentsdashboard')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:parentsdashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/parentslogin.html', {'form': form})

@login_required
def parents_dashboard_view(request):
    from attendance.models import Student, AttendanceRecord
    
    # Fetch children whose parent_email matches the current user's email
    children = Student.objects.filter(parent_email=request.user.email, is_active=True)
    
    # Get attendance records for all these children
    records = AttendanceRecord.objects.filter(
        student__in=children
    ).select_related('session', 'student').order_by('-session__date')
    
    # Calculate stats
    total_present = records.filter(status="Present").count()
    total_absent = records.filter(status="Absent").count()
    
    context = {
        'children': children,
        'records': records,
        'total_present': total_present,
        'total_absent': total_absent,
    }
    return render(request, 'attendance/parent_dashboard.html', context)





