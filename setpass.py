import os  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holbos_project.settings')  
  
import django  
django.setup()  
  
from django.contrib.auth.models import User  
  
# Set password for admin user  
user = User.objects.get(username='admin')  
user.set_password('admin123')  
user.save()  
print('Password set for admin: admin123')  
  
# Create test user  
if not User.objects.filter(username='testuser').exists():  
    user = User.objects.create_user(username='testuser', password='test123')  
    print(f'Created user: {user.username}')  
else:  
    user = User.objects.get(username='testuser')  
    user.set_password('test123')  
    user.save()  
    print(f'Updated password for: {user.username}')  
  
print()  
print('Login credentials:')  
print('  Admin: username=admin, password=admin123')  
print('  Test:  username=testuser, password=test123') 
