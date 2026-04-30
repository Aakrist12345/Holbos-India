from django.core.management.base import BaseCommand
from attendance.models import Student

STUDENTS = [

    ("Aarav Sharma",    "Class 1",  "C1-01"),
    ("Ananya Singh",    "Class 1",  "C1-02"),
    ("Arjun Verma",     "Class 1",  "C1-03"),
    ("Diya Patel",      "Class 1",  "C1-04"),
    ("Ishaan Mehta",    "Class 1",  "C1-05"),

    ("Kavya Nair",      "Class 2",  "C2-01"),
    ("Manav Gupta",     "Class 2",  "C2-02"),
    ("Neha Joshi",      "Class 2",  "C2-03"),
    ("Priya Reddy",     "Class 2",  "C2-04"),
    ("Rahul Kumar",     "Class 2",  "C2-05"),

    ("Riya Shah",       "Class 3",  "C3-01"),
    ("Rohan Das",       "Class 3",  "C3-02"),
    ("Saanvi Iyer",     "Class 3",  "C3-03"),
    ("Siddharth Roy",   "Class 3",  "C3-04"),
    ("Tanvi Bose",      "Class 3",  "C3-05"),

    ("Aditya Pandey",   "Class 4",  "C4-01"),
    ("Anvi Chaudhary",  "Class 4",  "C4-02"),
    ("Kabir Tiwari",    "Class 4",  "C4-03"),
    ("Mia Pillai",      "Class 4",  "C4-04"),
    ("Veer Malhotra",   "Class 4",  "C4-05"),

    ("Aadhya Khanna",   "Class 5",  "C5-01"),
    ("Aryan Mishra",    "Class 5",  "C5-02"),
    ("Divya Choudhary", "Class 5",  "C5-03"),
    ("Kiara Sethi",     "Class 5",  "C5-04"),
    ("Vivaan Jain",     "Class 5",  "C5-05"),
]

class Command(BaseCommand):
    help = "Seed sample students for Holbos AttendERP"

    def handle(self, *args, **kwargs):
        created = 0
        for name, cls, roll in STUDENTS:
            _, c = Student.objects.get_or_create(
                name=name, student_class=cls,
                defaults={"roll_number": roll}
            )
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new students ({len(STUDENTS)} total checked)."))
