"""
Тесты для представлений (views) приложения ads.
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.ads.models import Ad, Category, RentalRequest, Review


class HomeViewTest(TestCase):
    """Тесты для главной страницы."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")

    def test_home_view_status(self):
        """Главная страница возвращает 200."""
        response = self.client.get(reverse("ads:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_view_search(self):
        """Поиск на главной странице."""
        response = self.client.get(reverse("ads:home"), {"search": "тест"})
        self.assertEqual(response.status_code, 200)

    def test_home_view_filter_location(self):
        """Фильтрация по местоположению."""
        response = self.client.get(reverse("ads:home"), {"location": "москва"})
        self.assertEqual(response.status_code, 200)

    def test_home_view_filter_price(self):
        """Фильтрация по цене."""
        response = self.client.get(
            reverse("ads:home"), {"min_price": "1500", "max_price": "3000"}
        )
        self.assertEqual(response.status_code, 200)


class AdDetailViewTest(TestCase):
    """Тесты для страницы деталей объявления."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")
        self.ad = Ad.objects.create(
            owner=self.user,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )

    def test_ad_detail_view_status(self):
        """Страница деталей объявления возвращает 200."""
        response = self.client.get(reverse("ads:detail", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 200)

    def test_add_review_not_owner(self):
        """Добавление отзыва не владельцем."""
        moderator = User.objects.create_user(
            username="moderator", password="testpass123"
        )
        self.client.login(username="moderator", password="testpass123")
        response = self.client.post(
            reverse("ads:detail", kwargs={"pk": self.ad.pk}),
            {"rating": 5, "comment": "Отличное объявление!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(ad=self.ad, author=moderator).exists())

    def test_add_review_owner(self):
        """Добавление отзыва владельцем запрещено."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("ads:detail", kwargs={"pk": self.ad.pk}),
            {"rating": 5, "comment": "Свой отзыв"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(ad=self.ad, author=self.user).exists())


class AdManagementViewsTest(TestCase):
    """Тесты для управления объявлениями."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.moderator = User.objects.create_user(
            username="moderator", password="testpass123"
        )
        self.moderator.profile.is_moderator = True
        self.moderator.profile.save()

        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")

        self.ad = Ad.objects.create(
            owner=self.user,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        self.pending_ad = Ad.objects.create(
            owner=self.user,
            title="На модерации",
            description="Описание",
            price=Decimal("2000.00"),
            location="СПб",
            image=self.image,
            status="pending",
            category=self.category,
        )

    def test_create_ad_view_authenticated(self):
        """Создание объявления авторизованным пользователем."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("ads:create"))
        self.assertEqual(response.status_code, 200)

    def test_create_ad_view_unauthenticated(self):
        """Создание объявления неавторизованным перенаправляет."""
        response = self.client.get(reverse("ads:create"))
        self.assertEqual(response.status_code, 302)

    def test_edit_ad_view_owner(self):
        """Редактирование объявления владельцем."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("ads:edit", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_ad_view_not_owner(self):
        """Редактирование объявления не владельцем."""
        self.client.login(username="moderator", password="testpass123")
        response = self.client.get(reverse("ads:edit", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 404)

    def test_delete_ad_view(self):
        """Удаление объявления владельцем."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("ads:delete", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_mark_as_rented_view(self):
        """Отметка объявления как сданного."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("ads:rented", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.get(pk=self.ad.pk).status, "rented")

    def test_moderate_view_moderator(self):
        """Модерация объявлений модератором."""
        self.client.login(username="moderator", password="testpass123")
        response = self.client.get(reverse("ads:moderate"))
        self.assertEqual(response.status_code, 200)

    def test_moderate_view_not_moderator(self):
        """Модерация обычным пользователем перенаправляет."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("ads:moderate"))
        self.assertEqual(response.status_code, 302)

    def test_moderate_approve(self):
        """Одобрение объявления модератором."""
        self.client.login(username="moderator", password="testpass123")
        response = self.client.post(
            reverse("ads:moderate"), {"ad_id": self.pending_ad.pk, "action": "approve"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.get(pk=self.pending_ad.pk).status, "approved")

    def test_moderate_reject(self):
        """Отклонение объявления модератором."""
        self.client.login(username="moderator", password="testpass123")
        response = self.client.post(
            reverse("ads:moderate"), {"ad_id": self.pending_ad.pk, "action": "reject"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.get(pk=self.pending_ad.pk).status, "rejected")


class RentalRequestViewsTest(TestCase):
    """Тесты для представлений заявок на аренду."""

    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="testpass123")
        self.renter = User.objects.create_user(
            username="renter", password="testpass123"
        )
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
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

    def test_create_rental_request_authenticated(self):
        """Создание заявки авторизованным пользователем."""
        self.client.login(username="renter", password="testpass123")
        response = self.client.get(reverse("ads:detail", kwargs={"pk": self.ad.pk}))
        self.assertEqual(response.status_code, 200)

    def test_create_rental_request_own_ad(self):
        """Создание заявки на своё объявление запрещено."""
        self.client.login(username="owner", password="testpass123")
        response = self.client.post(
            reverse("ads:create_rental_request", kwargs={"pk": self.ad.pk}),
            {"start_date": "2026-04-01", "end_date": "2026-04-05"},
        )
        self.assertEqual(response.status_code, 302)

    def test_my_requests_view(self):
        """Просмотр своих заявок."""
        self.client.login(username="renter", password="testpass123")
        response = self.client.get(reverse("ads:my_requests"))
        self.assertEqual(response.status_code, 200)

    def test_respond_to_request_owner(self):
        """Ответ на заявку владельцем."""
        self.client.login(username="owner", password="testpass123")
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date="2026-04-01",
            end_date="2026-04-05",
        )
        response = self.client.post(
            reverse("ads:respond_to_request", kwargs={"pk": request.pk}),
            {"action": "accept"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RentalRequest.objects.get(pk=request.pk).status, "accepted")

    def test_respond_to_request_not_owner(self):
        """Ответ на заявку не владельцем запрещён."""
        self.client.login(username="renter", password="testpass123")
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date="2026-04-01",
            end_date="2026-04-05",
        )
        response = self.client.post(
            reverse("ads:respond_to_request", kwargs={"pk": request.pk}),
            {"action": "accept"},
        )
        self.assertEqual(response.status_code, 302)
