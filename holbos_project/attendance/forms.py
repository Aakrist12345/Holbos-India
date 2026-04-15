from django import forms
from django.contrib.auth import authenticate
from .models import Trainer, Student, AttendanceRecord


class TrainerSignupForm(forms.ModelForm):
    password  = forms.CharField(widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model  = Trainer
        fields = ["full_name", "username", "email"]

    def clean_username(self):
        uname = self.cleaned_data["username"]
        if Trainer.objects.filter(username=uname).exists():
            raise forms.ValidationError("Username already taken.")
        return uname

    def clean(self):
        cd = super().clean()
        if cd.get("password") != cd.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cd

    def save(self, commit=True):
        trainer = super().save(commit=False)
        trainer.set_password(self.cleaned_data["password"])
        if commit:
            trainer.save()
        return trainer


class TrainerLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd  = super().clean()
        user = authenticate(username=cd.get("username"), password=cd.get("password"))
        if not user:
            raise forms.ValidationError("Invalid username or password.")
        self.trainer = user
        return cd


class StudentForm(forms.ModelForm):
    class Meta:
        model  = Student
        fields = ["name", "student_class", "roll_number", "parent_email"]
