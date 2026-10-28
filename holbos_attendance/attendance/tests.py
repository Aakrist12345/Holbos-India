import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command, CommandError
from django.test import TestCase, Client
from django.urls import reverse
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


class BootstrapAdminCommandTests(TestCase):
    username = "render-admin"
    email = "render-admin@example.com"
    initial_password = "A-strong-initial-admin-password-482!"

    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {
                "DJANGO_SUPERUSER_USERNAME": self.username,
                "DJANGO_SUPERUSER_EMAIL": self.email,
                "DJANGO_SUPERUSER_PASSWORD": self.initial_password,
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_creates_admin_and_login_authenticates(self):
        output = StringIO()
        call_command("bootstrap_admin", stdout=output)
        user = get_user_model().objects.get(username=self.username)

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(self.initial_password))
        self.assertNotIn(self.initial_password, output.getvalue())
        self.assertEqual(
            authenticate(username=self.username, password=self.initial_password),
            user,
        )

        response = self.client.post(
            reverse("attendance:trainer_login"),
            {"username": self.username, "password": self.initial_password},
        )
        self.assertRedirects(response, reverse("attendance:dashboard"))

    def test_rerun_does_not_change_existing_admin_password(self):
        call_command("bootstrap_admin", stdout=StringIO())
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "A-different-password-930!"

        call_command("bootstrap_admin", stdout=StringIO())

        user = get_user_model().objects.get(username=self.username)
        self.assertTrue(user.check_password(self.initial_password))
        self.assertFalse(user.check_password(os.environ["DJANGO_SUPERUSER_PASSWORD"]))

    def test_password_reset_requires_explicit_flag(self):
        call_command("bootstrap_admin", stdout=StringIO())
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "A-new-admin-password-713!"

        call_command("bootstrap_admin", reset_password=True, stdout=StringIO())

        user = get_user_model().objects.get(username=self.username)
        self.assertTrue(user.check_password(os.environ["DJANGO_SUPERUSER_PASSWORD"]))
        self.assertFalse(user.check_password(self.initial_password))

    def test_existing_non_admin_account_is_not_promoted_or_changed(self):
        User = get_user_model()
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.initial_password,
            full_name="Existing user",
        )

        with self.assertRaises(CommandError):
            call_command("bootstrap_admin", stdout=StringIO(), stderr=StringIO())

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.initial_password))

    def test_password_policy_is_enforced_before_creation(self):
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "123"

        with self.assertRaises(CommandError):
            call_command("bootstrap_admin", stdout=StringIO(), stderr=StringIO())

        self.assertFalse(
            get_user_model().objects.filter(username=self.username).exists()
        )

    def test_missing_credentials_skip_bootstrap(self):
        for key in (
            "DJANGO_SUPERUSER_USERNAME",
            "DJANGO_SUPERUSER_EMAIL",
            "DJANGO_SUPERUSER_PASSWORD",
        ):
            os.environ.pop(key, None)

        output = StringIO()
        call_command("bootstrap_admin", stdout=output)

        self.assertIn("bootstrap skipped", output.getvalue())

    def test_partial_credentials_fail_without_creating_account(self):
        os.environ.pop("DJANGO_SUPERUSER_PASSWORD", None)

        with self.assertRaises(CommandError):
            call_command("bootstrap_admin", stdout=StringIO(), stderr=StringIO())

        self.assertFalse(
            get_user_model().objects.filter(username=self.username).exists()
        )

    @patch.dict(os.environ, {"RENDER": "true"})
    def test_render_refuses_non_postgresql_database(self):
        with self.settings(IS_RENDER=True):
            with self.assertRaises(CommandError):
                call_command("bootstrap_admin", stdout=StringIO(), stderr=StringIO())

    def test_full_name_is_requested_for_interactive_superuser_creation(self):
        self.assertIn("full_name", get_user_model().REQUIRED_FIELDS)
