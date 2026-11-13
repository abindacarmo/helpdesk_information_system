from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginTests(TestCase):
    """T-01 and T-02: valid login redirects, wrong password shows error."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="reporter1",
            password="devpass123",
            role=User.Roles.REPORTER,
        )

    def test_t01_login_with_valid_credentials_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": "reporter1", "password": "devpass123"},
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_t02_login_with_wrong_password_shows_error(self):
        response = self.client.post(
            reverse("login"),
            {"username": "reporter1", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wrong username or password.")
        # No session must be established.
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AnonymousAccessTests(TestCase):
    """T-03: anonymous users are redirected to the login page."""

    def test_t03_anonymous_user_opening_tickets_redirects_to_login(self):
        response = self.client.get(reverse("tickets:ticket_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])