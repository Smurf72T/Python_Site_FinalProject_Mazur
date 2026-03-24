"""
Тесты для форм приложения users.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from apps.users.forms import ProfileForm, RegistrationForm


class RegistrationFormTest(TestCase):
    """Тесты для формы регистрации."""

    def test_registration_form_valid(self):
        """Валидная форма регистрации."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_saves_email(self):
        """Форма сохраняет email пользователя."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        form = RegistrationForm(data=form_data)
        user = form.save()
        self.assertEqual(user.email, "newuser@example.com")

    def test_registration_form_password_mismatch(self):
        """Несовпадение паролей."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "DifferentPass123!",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_weak_password(self):
        """Слабый пароль."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "123",
            "password2": "123",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_duplicate_username(self):
        """Дубликат имени пользователя."""
        User.objects.create_user(username="existing", password="pass")
        form_data = {
            "username": "existing",
            "email": "new@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class ProfileFormTest(TestCase):
    """Тесты для формы профиля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_profile_form_valid(self):
        """Валидная форма профиля."""
        form_data = {"phone": "+7 999 123-45-67", "location": "Москва"}
        form = ProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.phone, "+7 999 123-45-67")
        self.assertEqual(profile.location, "Москва")

    def test_profile_form_empty(self):
        """Форма профиля с пустыми значениями."""
        form_data = {"phone": "", "location": ""}
        form = ProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())
