from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [

    path("login/",     views.parent_login,   name="login"),
    path("erp/",       views.erp_dashboard,  name="erp"),

    path("",          views.trainer_login,   name="trainer_login"),
    path("signup/",   views.trainer_signup,  name="signup"),
    path("logout/",   views.trainer_logout,  name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("mark/",               views.mark_attendance,        name="mark"),
    path("api/students/",       views.get_students_for_class, name="api_students"),
    path("api/submit/",         views.submit_attendance,      name="api_submit"),

    path("records/",    views.records,      name="records"),

    path("students/",         views.student_list,  name="students"),
    path("students/add/",     views.add_student,   name="add_student"),
    path("students/<int:pk>/delete/", views.delete_student, name="delete_student"),

    path("parents/",         views.parents_list,  name="parents_list"),
    path("parents/add/",     views.create_parent, name="create_parent"),
    path("parents/<int:pk>/status-toggle/", views.delete_parent, name="delete_parent"),
    path("parents/<int:pk>/delete/", views.hard_delete_parent, name="hard_delete_parent"),
]
