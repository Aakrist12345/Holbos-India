from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PortfolioItem

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
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


@login_required
def attendance_view(request):
    return render(request, 'accounts/attendance.html')

@login_required
def upload_portfolio_item(request):
    if request.method == 'POST':
        item_type = request.POST.get('type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')

        if not title or not item_type:
            return JsonResponse({'error': 'Missing title or type'}, status=400)

        # Allow upload even without file for Article type
        if item_type != 'Article' and not file:
            return JsonResponse({'error': 'Missing file upload'}, status=400)

        item = PortfolioItem.objects.create(
            user=request.user,
            title=title,
            description=description,
            item_type=item_type,
            file=file
        )
        return JsonResponse({'message': 'Success', 'item_id': item.id})
    return JsonResponse({'error': 'Invalid method'}, status=405)