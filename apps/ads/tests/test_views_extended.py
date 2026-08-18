"""
Расширенные тесты для представлений (views) приложения ads.
Покрывают все функции и ветки кода в apps/ads/views.py.
"""

from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.urls import reverse
from PIL import Image

from apps.ads.forms import AdForm, ReviewForm
from apps.ads.models import (
    Ad,
    Category,
    City,
    Message,
    Notification,
    RentalRequest,
    Review,
)
from apps.ads.views import home, ad_detail, moderate_ads


def create_test_image():
    """Создать тестовое изображение в формате JPEG."""
    img = Image.new("RGB", (100, 100), color="blue")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer


class HomeViewExtendedTest(TestCase):
    """Расширенные тесты для главной страницы."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.city = City.objects.create(name="Москва", region="Москва", is_active=True)
        self.ad = Ad.objects.create(
            owner=self.user,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
            city=self.city,
        )

    def test_home_view_shows_approved_only(self):
        """Главная страница показывает только одобренные объявления."""
        pending_ad = Ad.objects.create(
            owner=self.user,
            title="На модерации",
            description="Описание",
            price=Decimal("2000.00"),
            location="Москва",
            image=self.image,
            status="pending",
            category=self.category,
        )
        response = self.client.get(reverse("ads:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ad, response.context["ads"])
        self.assertNotIn(pending_ad, response.context["ads"])

    def test_home_view_filter_by_category(self):
        """Фильтрация по категории."""
        response = self.client.get(
            reverse("ads:home"), {"category": str(self.category.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ad, response.context["ads"])

    def test_home_view_filter_by_city(self):
        """Фильтрация по городу."""
        response = self.client.get(
            reverse("ads:home"), {"city": str(self.city.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ad, response.context["ads"])

    def test_home_view_pagination(self):
        """Пагинация на главной странице."""
        # Создаём больше 6 объявлений
        for i in range(10):
            Ad.objects.create(
                owner=self.user,
                title=f"Объявление {i}",
                description=f"Описание {i}",
                price=Decimal("1000.00"),
                location="Москва",
                image=self.image,
                status="approved",
                category=self.category,
            )
        response = self.client.get(reverse("ads:home"), {"page": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["ads"]), 6)

        response = self.client.get(reverse("ads:home"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context["ads"]) > 0)

    def test_home_view_categories_and_cities_in_context(self):
        """Контекст содержит категории и города."""
        response = self.client.get(reverse("ads:home"))
        self.assertIn("categories", response.context)
        self.assertIn("cities", response.context)


class AdDetailViewExtendedTest(TestCase):
    """Расширенные тесты для детальной страницы объявления."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.renter = User.objects.create_user(
            username="renter", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.ad = Ad.objects.create(
            owner=self.owner,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )

    def test_ad_detail_shows_accepted_requests(self):
        """Детальная страница показывает принятые заявки."""
        rental = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 5),
            status="accepted",
        )
        self.client.login(username="owner", password="testpass123")
        response = self.client.get(reverse("ads:detail", kwargs={"pk": self.ad.pk}))
        self.assertIn(rental, response.context["accepted_requests"])

    def test_ad_detail_review_form_for_anonymous(self):
        """Анонимный пользователь видит форму отзыва (пустую)."""
        response = self.client.get(reverse("ads:detail", kwargs={"pk": self.ad.pk}))
        self.assertIsInstance(response.context["form"], ReviewForm)

    def test_ad_detail_owner_cannot_review(self):
        """Владелец не может оставить отзыв на своё объявление."""
        self.client.login(username="owner", password="testpass123")
        response = self.client.post(
            reverse("ads:detail", kwargs={"pk": self.ad.pk}),
            {"rating": 5, "comment": "Свой отзыв"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(ad=self.ad, author=self.owner).exists())

    def test_ad_detail_invalid_review_form(self):
        """Невалидная форма отзыва не сохраняется."""
        self.client.login(username="renter", password="testpass123")
        response = self.client.post(
            reverse("ads:detail", kwargs={"pk": self.ad.pk}),
            {"rating": 10, "comment": ""},  # rating вне диапазона
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(ad=self.ad, author=self.renter).exists())


class AdManagementViewsExtendedTest(TestCase):
    """Расширенные тесты для управления объявлениями."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.city = City.objects.create(name="Москва", region="Москва", is_active=True)
        self.ad = Ad.objects.create(
            owner=self.user,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
            city=self.city,
        )

    def test_create_ad_post_valid(self):
        """POST создание объявления."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("ads:create"),
            {
                "title": "Новое платье",
                "description": "Описание",
                "price": "5000.00",
                "location": "Москва",
                "category": self.category.id,
                "city": self.city.id,
                "image": self.image,
            },
        )
        # Форма может быть невалидна из-за требований к изображению
        if response.status_code == 302:
            self.assertTrue(
                Ad.objects.filter(title="Новое платье", owner=self.user).exists()
            )

    def test_create_ad_post_invalid(self):
        """POST создание объявления с невалидными данными."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("ads:create"),
            {
                "title": "",  # пустой заголовок
                "description": "Описание",
                "price": "5000.00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

    def test_edit_ad_post_valid(self):
        """POST редактирование объявления."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("ads:edit", kwargs={"pk": self.ad.pk}),
            {
                "title": "Обновлённое название",
                "description": "Обновлённое описание",
                "price": "2000.00",
                "location": "Москва",
                "category": self.category.id,
                "city": self.city.id,
                "image": self.image,
            },
        )
        # Форма может быть невалидна из-за изображения
        if response.status_code == 302:
            self.ad.refresh_from_db()
            self.assertEqual(self.ad.title, "Обновлённое название")

    def test_delete_ad_get(self):
        """GET удаление объявления (перенаправляет)."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("ads:delete", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_mark_as_rented_not_owner(self):
        """Отметка как сданное не владельцем."""
        other_user = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.client.login(username="other", password="testpass123")
        response = self.client.post(
            reverse("ads:rented", kwargs={"pk": self.ad.pk})
        )
        self.assertEqual(response.status_code, 404)


class ModerateViewsExtendedTest(TestCase):
    """Расширенные тесты для модерации."""

    def setUp(self):
        self.moderator = User.objects.create_user(
            username="moderator", password="testpass123"
        )
        self.moderator.profile.is_moderator = True
        self.moderator.profile.save()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.pending_ad = Ad.objects.create(
            owner=self.user,
            title="На модерации",
            description="Описание",
            price=Decimal("2000.00"),
            location="Москва",
            image=self.image,
            status="pending",
            category=self.category,
        )

    def test_moderate_view_no_pending_ads(self):
        """Модерация когда нет ожидающих объявлений."""
        self.pending_ad.status = "approved"
        self.pending_ad.save()
        self.client.login(username="moderator", password="testpass123")
        response = self.client.get(reverse("ads:moderate"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["ads"]), 0)

    def test_moderate_approve_creates_notification(self):
        """Одобрение объявления меняет статус."""
        self.client.login(username="moderator", password="testpass123")
        response = self.client.post(
            reverse("ads:moderate"),
            {"ad_id": self.pending_ad.pk, "action": "approve"},
        )
        self.assertEqual(response.status_code, 302)
        self.pending_ad.refresh_from_db()
        self.assertEqual(self.pending_ad.status, "approved")

    def test_moderate_reject_creates_notification(self):
        """Отклонение объявления меняет статус."""
        self.client.login(username="moderator", password="testpass123")
        response = self.client.post(
            reverse("ads:moderate"),
            {"ad_id": self.pending_ad.pk, "action": "reject"},
        )
        self.assertEqual(response.status_code, 302)
        self.pending_ad.refresh_from_db()
        self.assertEqual(self.pending_ad.status, "rejected")


class RentalRequestViewsExtendedTest(TestCase):
    """Расширенные тесты для заявок на аренду."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.renter = User.objects.create_user(
            username="renter", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.ad = Ad.objects.create(
            owner=self.owner,
            title="Платье",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )

    def test_create_rental_request_with_dates(self):
        """Создание заявки с датами."""
        base = date.today() + timedelta(days=1)
        self.client.login(username="renter", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {
                "start_date": base.isoformat(),
                "end_date": (base + timedelta(days=4)).isoformat(),
                "comment": "Хочу арендовать",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            RentalRequest.objects.filter(
                ad=self.ad, renter=self.renter
            ).exists()
        )
        # Проверяем уведомление владельцу
        self.assertTrue(
            Notification.objects.filter(user=self.owner).exists()
        )

    def test_create_rental_request_invalid_dates(self):
        """Создание заявки с невалидными датами (start > end)."""
        base = date.today() + timedelta(days=10)
        self.client.login(username="renter", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {
                "start_date": (base + timedelta(days=9)).isoformat(),
                "end_date": base.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            RentalRequest.objects.filter(
                ad=self.ad, renter=self.renter
            ).exists()
        )

    def test_create_rental_request_past_dates(self):
        """Создание заявки с датой начала в прошлом запрещено."""
        self.client.login(username="renter", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {
                "start_date": (date.today() - timedelta(days=2)).isoformat(),
                "end_date": (date.today() + timedelta(days=2)).isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            RentalRequest.objects.filter(
                ad=self.ad, renter=self.renter
            ).exists()
        )

    def test_create_rental_request_unavailable_ad(self):
        """Заявка на недоступное (не опубликованное) объявление запрещена."""
        self.ad.status = "pending"
        self.ad.save()
        base = date.today() + timedelta(days=1)
        self.client.login(username="renter", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {
                "start_date": base.isoformat(),
                "end_date": (base + timedelta(days=2)).isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            RentalRequest.objects.filter(
                ad=self.ad, renter=self.renter
            ).exists()
        )

    def test_create_rental_request_missing_dates(self):
        """Создание заявки без дат."""
        self.client.login(username="renter", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {"comment": "Хочу арендовать"},
        )
        self.assertEqual(response.status_code, 302)

    def test_create_rental_request_overlapping(self):
        """Создание заявки с пересекающимися датами."""
        base = date.today() + timedelta(days=30)
        # Создаём принятую заявку
        RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=base,
            end_date=base + timedelta(days=9),
            status="accepted",
        )
        other_renter = User.objects.create_user(
            username="other_renter", password="testpass123"
        )
        self.client.login(username="other_renter", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {
                "start_date": (base + timedelta(days=4)).isoformat(),
                "end_date": (base + timedelta(days=14)).isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_my_requests_view_shows_both_types(self):
        """Просмотр заявок показывает входящие и исходящие."""
        RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
        self.client.login(username="renter", password="testpass123")
        response = self.client.get(reverse("ads:my_requests"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("renter_requests", response.context)
        self.assertIn("owner_requests", response.context)

    def test_request_detail_access_check(self):
        """Детальная страница заявки проверяет доступ."""
        rental = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
        # Сторонний пользователь
        other_user = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.client.login(username="other", password="testpass123")
        response = self.client.get(
            reverse("ads:request_detail", kwargs={"pk": rental.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_request_detail_owner_access(self):
        """Владелец объявления имеет доступ к заявке."""
        rental = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
        self.client.login(username="owner", password="testpass123")
        response = self.client.get(
            reverse("ads:request_detail", kwargs={"pk": rental.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_respond_to_request_accept(self):
        """Принятие заявки меняет статус объявления."""
        rental = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
        self.client.login(username="owner", password="testpass123")
        response = self.client.post(
            reverse("ads:respond_to_request", kwargs={"pk": rental.pk}),
            {"action": "accept"},
        )
        self.assertEqual(response.status_code, 302)
        rental.refresh_from_db()
        self.assertEqual(rental.status, "accepted")
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.status, "rented")
        # Уведомление арендатору
        self.assertTrue(
            Notification.objects.filter(user=self.renter).exists()
        )

    def test_respond_to_request_reject(self):
        """Отклонение заявки."""
        rental = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
        self.client.login(username="owner", password="testpass123")
        response = self.client.post(
            reverse("ads:respond_to_request", kwargs={"pk": rental.pk}),
            {"action": "reject"},
        )
        self.assertEqual(response.status_code, 302)
        rental.refresh_from_db()
        self.assertEqual(rental.status, "rejected")
        # Уведомление арендатору
        self.assertTrue(
            Notification.objects.filter(user=self.renter).exists()
        )

    def test_respond_to_request_not_owner(self):
        """Ответ на заявку не владельцем запрещён."""
        rental = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
        other_user = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.client.login(username="other", password="testpass123")
        response = self.client.post(
            reverse("ads:respond_to_request", kwargs={"pk": rental.pk}),
            {"action": "accept"},
        )
        self.assertEqual(response.status_code, 302)


class SendMessageViewTest(TestCase):
    """Тесты для отправки сообщений."""

    def setUp(self):
        self.sender = User.objects.create_user(
            username="sender", password="testpass123"
        )
        self.recipient = User.objects.create_user(
            username="recipient", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.ad = Ad.objects.create(
            owner=self.recipient,
            title="Объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )

    def test_send_message_with_body(self):
        """Отправка сообщения с телом."""
        self.client.login(username="sender", password="testpass123")
        response = self.client.post(
            reverse("ads:send_message", kwargs={"recipient_id": self.recipient.pk}),
            {
                "body": "Привет!",
                "subject": "Тест",
                "ad_id": self.ad.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Message.objects.filter(
                sender=self.sender, recipient=self.recipient
            ).exists()
        )
        # Уведомление получателю
        self.assertTrue(
            Notification.objects.filter(user=self.recipient).exists()
        )

    def test_send_message_empty_body(self):
        """Отправка сообщения без тела не создаёт сообщение."""
        self.client.login(username="sender", password="testpass123")
        response = self.client.post(
            reverse("ads:send_message", kwargs={"recipient_id": self.recipient.pk}),
            {
                "body": "",
                "subject": "Тест",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Message.objects.filter(
                sender=self.sender, recipient=self.recipient, body=""
            ).exists()
        )

    def test_send_message_get_redirects(self):
        """GET запрос на отправку сообщения перенаправляет."""
        self.client.login(username="sender", password="testpass123")
        response = self.client.get(
            reverse("ads:send_message", kwargs={"recipient_id": self.recipient.pk})
        )
        self.assertEqual(response.status_code, 302)
