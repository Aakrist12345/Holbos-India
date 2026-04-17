from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class TrainerManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class Trainer(AbstractBaseUser, PermissionsMixin):
    username   = models.CharField(max_length=100, unique=True)
    full_name  = models.CharField(max_length=200)
    email      = models.EmailField(unique=True)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Prevent reverse accessor clashes with Django's built-in auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='trainer_set',
        related_query_name='trainer',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='trainer_set',
        related_query_name='trainer',
    )

    objects = TrainerManager()

    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.full_name or self.username


CLASS_CHOICES = [(f"Class {i}", f"Class {i}") for i in range(1, 11)]


class Student(models.Model):
    name       = models.CharField(max_length=200)
    student_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    roll_number = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["student_class", "name"]

    def __str__(self):
        return f"{self.name} ({self.student_class})"


STATUS_CHOICES = [("Present", "Present"), ("Absent", "Absent")]


class AttendanceSession(models.Model):
    trainer       = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="sessions")
    student_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    date          = models.DateField()
    submitted_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student_class", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student_class} — {self.date}"

    @property
    def present_count(self):
        return self.records.filter(status="Present").count()

    @property
    def absent_count(self):
        return self.records.filter(status="Absent").count()


class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance")
    status  = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Present")

    class Meta:
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student.name} — {self.status} on {self.session.date}"
