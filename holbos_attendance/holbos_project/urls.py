from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponse
from django.core.mail import send_mail


def test_email(request):
    try:
        result = send_mail(
            "Holbos Test Email",
            "This is a test email from Render.",
            settings.DEFAULT_FROM_EMAIL,
            ["Aakholbos7497@gmail.com"],
            fail_silently=False,
        )
        return HttpResponse(f"Email result: {result}")
    except Exception as e:
        return HttpResponse(f"Email error: {e}")


urlpatterns = [
    path('test-email/', test_email),

    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('modules/', include('modules.urls')),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url='/password-reset/done/',
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)