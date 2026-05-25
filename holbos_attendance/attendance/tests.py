from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from attendance.models import Student, CompensationBooking

User = get_user_model()

class BookingModalTest(TestCase):
    def setUp(self):
        # Create a trainer user (acting as parent)
        self.user = User.objects.create_user(username='parent1', email='parent1@example.com', password='testpass')
        # If there is a flag for parent, set it (optional)
        if not hasattr(self.user, 'is_parent'):
            setattr(self.user, 'is_parent', True)
        self.user.save()
        # Create a student linked to this parent
        self.student = Student.objects.create(name='Test Student', parent_email='parent1@example.com', parent_mobile='1234567890')
        self.client = Client()
        self.client.login(username='parent1', password='testpass')

    def test_booking_success_shows_modal(self):
        # Post a booking request for Saturday
        response = self.client.post(reverse('attendance:book_compensation', kwargs={'student_id': self.student.id}), {'day': 'Saturday'}, follow=True)
        # Check that the success message is present in the response
        self.assertContains(response, 'Your compensation slot for Saturday has been successfully booked')
        # Check that modal HTML is rendered
        self.assertContains(response, 'modal-backdrop')
        self.assertContains(response, 'Booking Confirmed!')
