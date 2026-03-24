"""
Тесты для представлений (views) приложения users.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from apps.users.models import Profile


class UserAuthViewsTest(TestCase):
    """Тесты для представлений аутентификации."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_register_view_get(self):
        """Страница регистрации GET."""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post_valid(self):
        """Регистрация с валидными данными."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(reverse('users:register'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Страница входа GET."""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post_valid(self):
        """Вход с валидными данными."""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_view_post_invalid(self):
        """Вход с неверными данными."""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Выход из системы."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)


class ProfileViewsTest(TestCase):
    """Тесты для представлений профиля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_profile_view_authenticated(self):
        """Страница профиля для авторизованного."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        """Страница профиля для неавторизованного."""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_get(self):
        """Редактирование профиля GET."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_post(self):
        """Редактирование профиля POST."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:profile_edit'), {
            'phone': '+7 999 123-45-67',
            'location': 'Москва'
        })
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '+7 999 123-45-67')
        self.assertEqual(self.user.profile.location, 'Москва')


class MessageViewsTest(TestCase):
    """Тесты для представлений сообщений."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

    def test_messages_list_authenticated(self):
        """Список сообщений для авторизованного."""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('users:messages'))
        self.assertEqual(response.status_code, 200)

    def test_messages_list_unauthenticated(self):
        """Список сообщений для неавторизованного."""
        response = self.client.get(reverse('users:messages'))
        self.assertEqual(response.status_code, 302)

    def test_message_detail_view(self):
        """Просмотр диалога."""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('users:message_detail', kwargs={'user_id': self.user2.pk}))
        self.assertEqual(response.status_code, 200)

    def test_send_message(self):
        """Отправка сообщения."""
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('users:message_detail', kwargs={'user_id': self.user2.pk}), {
            'body': 'Привет!',
            'subject': 'Тест'
        })
        self.assertEqual(response.status_code, 302)
