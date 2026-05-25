from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ParentLoginRestrictionTests(TestCase):
    def setUp(self):
        # Create a parent user
        self.parent_user = User.objects.create_user(
            username="parent123",
            email="parent@example.com",
            password="testpassword123",
            is_parent=True,
            mobile_number="9876543210"
        )
        # Create a trainer user
        self.trainer_user = User.objects.create_user(
            username="trainer123",
            email="trainer@example.com",
            password="testpassword123",
            is_parent=False
        )

    def test_parent_can_login_via_parent_portal(self):
        login_url = reverse('accounts:parents_login')
        response = self.client.post(login_url, {
            'username': 'parent123',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('accounts:dashboard'))
        self.assertTrue(('_auth_user_id' in self.client.session))

    def test_trainer_cannot_login_via_parent_portal(self):
        login_url = reverse('accounts:parents_login')
        response = self.client.post(login_url, {
            'username': 'trainer123',
            'password': 'testpassword123'
        }, follow=True)
        self.assertFalse(('_auth_user_id' in self.client.session))
        self.assertContains(response, "Only parent accounts are allowed to log in through this portal.")

    def test_parent_cannot_login_via_trainer_portal(self):
        login_url = reverse('attendance:trainer_login')
        response = self.client.post(login_url, {
            'username': 'parent123',
            'password': 'testpassword123'
        }, follow=True)
        self.assertFalse(('_auth_user_id' in self.client.session))
        self.assertContains(response, "Parent accounts must use the Parent Login portal.")


class ParentForgotPasswordTests(TestCase):
    def setUp(self):
        self.parent_user = User.objects.create_user(
            username="parentforgot",
            email="parentforgot@example.com",
            password="oldpassword123",
            is_parent=True,
            mobile_number="9000000001"
        )
        self.forgot_url = reverse('accounts:parents_forgot_password')
        self.reset_url = reverse('accounts:parents_reset_password')

    def test_forgot_password_page_loads(self):
        response = self.client.get(self.forgot_url)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page_redirects_without_session(self):
        """Directly accessing reset page without session should redirect."""
        response = self.client.get(self.reset_url)
        self.assertRedirects(response, self.forgot_url)

    def test_forgot_password_valid_username_and_mobile(self):
        """Valid username + mobile should set session and redirect to reset page."""
        response = self.client.post(self.forgot_url, {
            'username': 'parentforgot',
            'mobile_number': '9000000001'
        })
        self.assertRedirects(response, self.reset_url)
        self.assertIn('reset_password_user_id', self.client.session)

    def test_forgot_password_wrong_mobile(self):
        """Wrong mobile number should show error and not set session."""
        response = self.client.post(self.forgot_url, {
            'username': 'parentforgot',
            'mobile_number': '0000000000'
        }, follow=True)
        self.assertNotIn('reset_password_user_id', self.client.session)
        self.assertContains(response, "No parent account matches the provided username and mobile number.")

    def test_forgot_password_wrong_username(self):
        """Non-existent username should show error."""
        response = self.client.post(self.forgot_url, {
            'username': 'doesnotexist',
            'mobile_number': '9000000001'
        }, follow=True)
        self.assertNotIn('reset_password_user_id', self.client.session)
        self.assertContains(response, "No parent account matches the provided username and mobile number.")

    def test_reset_password_success(self):
        """After verification, password should be reset successfully."""
        # Step 1: verify identity
        self.client.post(self.forgot_url, {
            'username': 'parentforgot',
            'mobile_number': '9000000001'
        })
        # Step 2: set new password
        response = self.client.post(self.reset_url, {
            'password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        self.assertRedirects(response, reverse('accounts:parents_login'))
        # Verify password actually changed
        self.parent_user.refresh_from_db()
        self.assertTrue(self.parent_user.check_password('newpassword456'))

    def test_reset_password_mismatch(self):
        """Mismatched passwords should show error."""
        self.client.post(self.forgot_url, {
            'username': 'parentforgot',
            'mobile_number': '9000000001'
        })
        response = self.client.post(self.reset_url, {
            'password': 'newpassword456',
            'confirm_password': 'wrongpassword'
        }, follow=True)
        self.assertContains(response, "Passwords do not match.")

    def test_reset_password_too_short(self):
        """Password less than 6 characters should show error."""
        self.client.post(self.forgot_url, {
            'username': 'parentforgot',
            'mobile_number': '9000000001'
        })
        response = self.client.post(self.reset_url, {
            'password': 'abc',
            'confirm_password': 'abc'
        }, follow=True)
        self.assertContains(response, "Password must be at least 6 characters long.")


class ParentOptionalEmailTests(TestCase):
    def test_create_parent_without_email(self):
        """Parent can be created with no email (None) and a mobile number."""
        parent = User.objects.create_user(
            username="noemailparent",
            email=None,
            password="pass123456",
            is_parent=True,
            mobile_number="9111111111"
        )
        parent.refresh_from_db()
        self.assertIsNone(parent.email)
        self.assertEqual(parent.mobile_number, "9111111111")

    def test_create_multiple_parents_without_email_no_unique_violation(self):
        """Multiple parents without emails should not cause UNIQUE constraint errors."""
        User.objects.create_user(
            username="noemail1", email=None, password="pass123456",
            is_parent=True, mobile_number="9222222221"
        )
        User.objects.create_user(
            username="noemail2", email=None, password="pass123456",
            is_parent=True, mobile_number="9222222222"
        )
        self.assertEqual(User.objects.filter(email__isnull=True, is_parent=True).count(), 2)
