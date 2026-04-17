from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Trainer, Student, AttendanceSession, AttendanceRecord


@admin.register(Trainer)
class TrainerAdmin(UserAdmin):
    list_display  = ("username", "full_name", "email", "is_staff", "date_joined")
    search_fields = ("username", "email", "full_name")
    ordering      = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("full_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {"fields": ("username", "full_name", "email", "password1", "password2")}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ("name", "student_class", "roll_number", "parent_email", "is_active")
    list_filter   = ("student_class", "is_active")
    search_fields = ("name", "roll_number")
    ordering      = ("student_class", "name")


class AttendanceRecordInline(admin.TabularInline):
    model  = AttendanceRecord
    extra  = 0
    fields = ("student", "status")


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("student_class", "date", "trainer", "present_count", "absent_count")
    list_filter  = ("student_class", "date")
    inlines      = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ("student", "session", "status")
    list_filter   = ("status", "session__student_class")
    search_fields = ("student__name",)
