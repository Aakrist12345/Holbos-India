from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def shivaji_view(request):
    return render(request, 'modules/shivaji.html')

@login_required
def doraemon_view(request):
    return render(request, 'modules/doraemon.html')

@login_required
def learning_blocks_view(request):
    return render(request, 'modules/learning_blocks.html')

@login_required
def science_view(request):
    return render(request, 'modules/science.html')

@login_required
def art_view(request):
    return render(request, 'modules/art.html')

@login_required
def math_view(request):
    return render(request, 'modules/math.html')
