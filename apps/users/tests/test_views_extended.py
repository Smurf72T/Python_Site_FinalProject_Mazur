"""
Расширенные тесты для представлений (views) приложения users.
Покрывают все функции и ветки кода в apps/users/views.py.
"""

from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.ads.models import Ad, Category, Message, Notification, RentalRequest


def create_test_image():
    """Создать тестовое изображение в формате JPEG."""
    img = Image.new("RGB", (100, 100), color="green")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer


class RegisterViewExtendedTest(TestCase):
    """Расширенные тесты для регистрации."""

    def test_register_post_invalid_data(self):
        """Регистрация с невалидными данными."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "",
                "email": "invalid",
                "password1": "short",
                "password2": "short",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

    def test_register_success_auto_login(self):
        """Успешная регистрация автоматически авторизует."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        # Проверяем что пользователь авторизован
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)


class ProfileViewExtendedTest(TestCase):
    """Расширенные тесты для профиля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")

    def test_profile_shows_user_ads(self):
        """Профиль показывает объявления пользователя."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Моё объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(ad, response.context["ads"])

    def test_profile_shows_rented_ads(self):
        """Профиль показывает арендованные объявления."""
        owner = User.objects.create_user(username="owner", password="pass123")
        ad = Ad.objects.create(
            owner=owner,
            title="Чужое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        RentalRequest.objects.create(
            ad=ad,
            renter=self.user,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
            status="accepted",
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context["rented_ads"]) > 0)

    def test_profile_shows_rented_out_ads(self):
        """Профиль показывает сданные объявления."""
        renter = User.objects.create_user(username="renter", password="pass123")
        ad = Ad.objects.create(
            owner=self.user,
            title="Моё объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        RentalRequest.objects.create(
            ad=ad,
            renter=renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
            status="accepted",
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context["rented_out_ads"]) > 0)


class ProfileEditViewExtendedTest(TestCase):
    """Расширенные тесты для редактирования профиля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_profile_edit_post_valid(self):
        """POST редактирование профиля с валидными данными."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "phone": "+7 999 123-45-67",
                "location": "Санкт-Петербург",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, "+7 999 123-45-67")
        self.assertEqual(self.user.profile.location, "Санкт-Петербург")

    def test_profile_edit_post_invalid(self):
        """POST редактирование профиля с невалидными данными."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "phone": "+7 999 123-45-67",
                "location": "Москва",
                "bio": "A" * 501,  # Превышение max_length
            },
        )
        # Форма может быть невалидна из-за bio > 500 символов
        self.user.profile.refresh_from_db()
        # Проверяем что bio не изменился (пустой)
        self.assertEqual(self.user.profile.bio, "")

    def test_profile_edit_shows_ads_in_context(self):
        """Редактирование профиля показывает объявления в контексте."""
        image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        category = Category.objects.create(name="Платья")
        Ad.objects.create(
            owner=self.user,
            title="Моё объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=image,
            status="approved",
            category=category,
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("ads", response.context)
        self.assertTrue(len(response.context["ads"]) > 0)


class MessagesListViewExtendedTest(TestCase):
    """Расширенные тесты для списка сообщений."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            username="user3", password="testpass123"
        )

    def test_messages_list_empty(self):
        """Список сообщений пустой."""
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(reverse("users:messages"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["conversations"]), 0)

    def test_messages_list_with_sent_messages(self):
        """Список сообщений с отправленными сообщениями."""
        Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            subject="Тест",
            body="Привет!",
        )
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(reverse("users:messages"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["conversations"]), 1)

    def test_messages_list_with_received_messages(self):
        """Список сообщений с полученными сообщениями."""
        Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            subject="Тест",
            body="Привет!",
        )
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(reverse("users:messages"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["conversations"]), 1)

    def test_messages_list_unread_count(self):
        """Список сообщений показывает непрочитанные."""
        Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            subject="Тест",
            body="Привет!",
            is_read=False,
        )
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(reverse("users:messages"))
        self.assertEqual(response.status_code, 200)
        conv = response.context["conversations"][0]
        self.assertEqual(conv["unread_count"], 1)

    def test_messages_list_marks_notifications_read(self):
        """Просмотр сообщений помечает уведомления как прочитанные."""
        Notification.objects.create(
            user=self.user1,
            title="Новое сообщение",
            message="Тест",
            notification_type="info",
            is_read=False,
        )
        self.client.login(username="user1", password="testpass123")
        self.client.get(reverse("users:messages"))
        self.assertFalse(
            Notification.objects.filter(
                user=self.user1, title="Новое сообщение", is_read=False
            ).exists()
        )

    def test_messages_list_sorts_by_last_message(self):
        """Список сообщений сортирован по дате последнего."""
        msg_old = Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            subject="Старое",
            body="Старое сообщение",
        )
        # Меняем created_at для тестирования сортировки
        Message.objects.filter(pk=msg_old.pk).update(
            created_at="2026-01-01 00:00:00+00:00"
        )

        msg_new = Message.objects.create(
            sender=self.user3,
            recipient=self.user1,
            subject="Новое",
            body="Новое сообщение",
        )

        self.client.login(username="user1", password="testpass123")
        response = self.client.get(reverse("users:messages"))
        self.assertEqual(response.status_code, 200)
        conversations = response.context["conversations"]
        self.assertEqual(len(conversations), 2)
        # Первое сообщение — более новое
        self.assertEqual(conversations[0]["user"], msg_new.sender)


class MessageDetailViewExtendedTest(TestCase):
    """Расширенные тесты для детальной страницы сообщений."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="testpass123"
        )

    def test_message_detail_shows_conversation(self):
        """Детальная страница показывает диалог."""
        Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            subject="Тест",
            body="Привет от user1!",
        )
        Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            subject="Тест",
            body="Привет от user2!",
        )
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(
            reverse("users:message_detail", kwargs={"user_id": self.user2.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["messages"]), 2)

    def test_message_detail_marks_read(self):
        """Детальная страница помечает сообщения как прочитанные."""
        Message.objects.create(
            sender=self.user2,
            recipient=self.user1,
            subject="Тест",
            body="Привет!",
            is_read=False,
        )
        self.client.login(username="user1", password="testpass123")
        self.client.get(
            reverse("users:message_detail", kwargs={"user_id": self.user2.pk})
        )
        self.assertFalse(
            Message.objects.filter(
                sender=self.user2, recipient=self.user1, is_read=False
            ).exists()
        )

    def test_message_detail_send_new_message(self):
        """Отправка нового сообщения в диалоге."""
        self.client.login(username="user1", password="testpass123")
        response = self.client.post(
            reverse("users:message_detail", kwargs={"user_id": self.user2.pk}),
            {"body": "Новое сообщение в диалоге", "subject": "Ответ"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Message.objects.filter(
                sender=self.user1,
                recipient=self.user2,
                body="Новое сообщение в диалоге",
            ).exists()
        )

    def test_message_detail_send_without_ad(self):
        """Отправка сообщения без привязки к объявлению."""
        self.client.login(username="user1", password="testpass123")
        response = self.client.post(
            reverse("users:message_detail", kwargs={"user_id": self.user2.pk}),
            {"body": "Сообщение без объявления"},
        )
        self.assertEqual(response.status_code, 302)
        msg = Message.objects.get(
            sender=self.user1, recipient=self.user2, body="Сообщение без объявления"
        )
        self.assertIsNone(msg.ad)

    def test_message_detail_send_empty_body(self):
        """Отправка сообщения с пустым телом не создаёт сообщение."""
        self.client.login(username="user1", password="testpass123")
        count_before = Message.objects.count()
        response = self.client.post(
            reverse("users:message_detail", kwargs={"user_id": self.user2.pk}),
            {"body": "", "subject": "Пустое"},
        )
        # View может возвращать 200 или 302
        self.assertIn(response.status_code, [200, 302])
        # Но сообщение не создаётся
        self.assertEqual(Message.objects.count(), count_before)
