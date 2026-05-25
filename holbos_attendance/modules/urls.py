from django.urls import path
from . import views

urlpatterns = [
    path('shivaji/', views.shivaji_view, name='shivaji'),
    path('doraemon/', views.doraemon_view, name='doraemon'),
    path('learning-blocks/', views.learning_blocks_view, name='learning_blocks'),
    path('science/', views.science_view, name='science'),
    path('art/', views.art_view, name='art'),
    path('math/', views.math_view, name='math'),
]