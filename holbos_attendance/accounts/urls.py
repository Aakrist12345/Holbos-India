from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('parents-login/', views.parents_login_view, name='parents_login'),
    path('parents-signup/', views.parents_signup_view, name='parents_signup'),
    path('parents-dashboard/', views.parents_dashboard_view, name='parentsdashboard'),
    path('upload-portfolio/', views.upload_portfolio, name='upload_portfolio'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('parents-forgot-password/', views.parents_forgot_password_view, name='parents_forgot_password'),
    path('parents-reset-password/', views.parents_reset_password_view, name='parents_reset_password'),
]
