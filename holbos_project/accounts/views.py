from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')
    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def attendance_view(request):
    return render(request, 'accounts/attendance.html')
def parents_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('parentsdashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('parents_login')
    return render(request, 'accounts/parentslogin.html')

@login_required
def parents_dashboard_view(request):
    return render(request, 'accounts/parentsdashboard.html')




