from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    # Auth
    path("",          views.trainer_login,   name="login"),
    path("signup/",   views.trainer_signup,  name="signup"),
    path("logout/",   views.trainer_logout,  name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Mark attendance
    path("mark/",               views.mark_attendance,        name="mark"),
    path("api/students/",       views.get_students_for_class, name="api_students"),
    path("api/submit/",         views.submit_attendance,      name="api_submit"),

    # Records
    path("records/",    views.records,      name="records"),

    # Students
    path("students/",         views.student_list,  name="students"),
    path("students/add/",     views.add_student,   name="add_student"),
    path("students/<int:pk>/delete/", views.delete_student, name="delete_student"),
]
