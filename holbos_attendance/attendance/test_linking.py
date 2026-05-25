import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holbos_project.settings')
django.setup()

from attendance.models import Trainer, Student
from django.db import transaction

def main():
    # Clean up previous test objects
    Trainer.objects.filter(username='testparent').delete()
    Student.objects.filter(name='Test Student').delete()
    # Create a trainer (parent) with email and mobile
    parent = Trainer.objects.create_user(username='testparent', password='testpass123', email='parent@example.com', mobile_number='1234567890')
    # Create a student linked via email
    student = Student.objects.create(name='Test Student', student_class='Class 1', parent_email='parent@example.com')
    # Verify linking
    linked = parent.get_linked_students()
    print('Linked students count:', linked.count())
    for s in linked:
        print('Linked student:', s.name, s.parent_email, s.parent_mobile)

if __name__ == '__main__':
    with transaction.atomic():
        main()
