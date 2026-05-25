import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holbos_project.settings')

django.setup()

from attendance.models import Trainer, Student

def main():
    # Clean any previous test data
    Trainer.objects.filter(username='testparent').delete()
    Student.objects.filter(name='Test Student').delete()

    # Create a parent trainer
    parent = Trainer.objects.create_user(
        username='testparent',
        password='testpass123',
        email='parent@example.com',
        mobile_number='5551234567',
        is_parent=True,
    )
    # Create a linked student (by email)
    Student.objects.create(
        name='Test Student',
        student_class='Class 1',
        parent_email='parent@example.com',
        parent_mobile='',
        is_active=True,
    )
    # Use the helper to fetch linked students
    linked_qs = parent.get_linked_students()
    print('Linked count:', linked_qs.count())
    for s in linked_qs:
        print('Linked student:', s.name, s.parent_email, s.parent_mobile)

if __name__ == '__main__':
    main()
