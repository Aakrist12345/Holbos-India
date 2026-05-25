from django import forms
from django.contrib.auth import authenticate
from .models import Trainer, Student

class TrainerSignupForm(forms.ModelForm):
    email = forms.EmailField(required=True)
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
        fields = ["name", "student_class", "section", "parent_mobile"]

    def clean_parent_mobile(self):
        mobile = self.cleaned_data.get("parent_mobile")
        if not mobile:
            return mobile
        if not Trainer.objects.filter(mobile_number=mobile, is_parent=True).exists():
            raise forms.ValidationError("No parent account found for the provided mobile number.")
        return mobile

class ParentCreateForm(forms.Form):
    full_name = forms.CharField(max_length=200)
    username  = forms.CharField(max_length=100)
    email     = forms.EmailField(required=False)
    mobile_number = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter registered mobile number'})
    )
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if not uname:
            return uname
        if Trainer.objects.filter(username=uname).exists():
            raise forms.ValidationError("Username already taken.")
        return uname

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        if Trainer.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already associated with an account.")
        return email

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number")
        if not mobile:
            return None
        if Trainer.objects.filter(mobile_number=mobile).exists():
            raise forms.ValidationError("Mobile number already associated with an account.")
        return mobile

    def clean(self):
        cd = super().clean()
        if cd.get("password1") != cd.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cd

    def save(self):
        cd = self.cleaned_data
        email = cd.get("email") or None
        parent = Trainer.objects.create_user(
            username=cd["username"],
            email=email,
            password=cd["password1"],
            full_name=cd["full_name"],
            mobile_number=cd["mobile_number"],
            is_parent=True,
        )
        return parent
