from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('parents-login/', views.parents_login_view, name='parents_login'),
    path('parents-dashboard/', views.parents_dashboard_view, name='parentsdashboard'),
]
