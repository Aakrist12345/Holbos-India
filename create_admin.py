import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holbos_project.settings')
django.setup()

from django.contrib.auth.models import User

# Create or update admin user with specified credentials
username = 'aakristsharma135@gmail.com'
email = 'aakristsharma135@gmail.com'
password = '123qweasE@'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'✓ Updated existing user: {username}')
except User.DoesNotExist:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✓ Created new superuser: {username}')

print('\n' + '='*50)
print('BACKEND ACCESS CREDENTIALS')
print('='*50)
print(f'Email/Username: {username}')
print(f'Password: {password}')
print(f'Admin URL: http://127.0.0.1:8000/admin/')
print('='*50)
