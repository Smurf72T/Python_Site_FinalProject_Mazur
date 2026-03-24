"""
Тесты для сервисных функций приложения ads.
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.ads.models import Ad, Category
from apps.ads.services import (approve_ad_instance, get_filtered_ads,
                               reject_ad_instance)


class ServicesTest(TestCase):
    """Тесты для сервисных функций."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.category = Category.objects.create(name="Платья")

    def test_get_filtered_ads_search(self):
        """Фильтрация по поиску."""
        Ad.objects.create(
            owner=self.user,
            title="Вечернее платье",
            description="Красивое платье",
            price=Decimal("5000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        Ad.objects.create(
            owner=self.user,
            title="Костюм",
            description="Деловой костюм",
            price=Decimal("3000.00"),
            location="СПб",
            image=self.image,
            status="approved",
            category=self.category,
        )

        ads = Ad.objects.filter(status="approved")
        filtered = get_filtered_ads(ads, search="платье")

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, "Вечернее платье")

    def test_get_filtered_ads_location(self):
        """Фильтрация по местоположению."""
        Ad.objects.create(
            owner=self.user,
            title="Объявление 1",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        Ad.objects.create(
            owner=self.user,
            title="Объявление 2",
            description="Описание",
            price=Decimal("1000.00"),
            location="СПб",
            image=self.image,
            status="approved",
            category=self.category,
        )

        ads = Ad.objects.filter(status="approved")
        filtered = get_filtered_ads(ads, location="москва")

        self.assertEqual(filtered.count(), 1)

    def test_get_filtered_ads_price_range(self):
        """Фильтрация по цене."""
        Ad.objects.create(
            owner=self.user,
            title="Дешевое",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )
        Ad.objects.create(
            owner=self.user,
            title="Дорогое",
            description="Описание",
            price=Decimal("10000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            category=self.category,
        )

        ads = Ad.objects.filter(status="approved")
        filtered = get_filtered_ads(ads, min_price="5000", max_price="15000")

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().price, Decimal("10000.00"))

    def test_approve_ad_instance(self):
        """Одобрение объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="pending",
            category=self.category,
        )
        approved = approve_ad_instance(ad)
        self.assertEqual(approved.status, "approved")

    def test_reject_ad_instance(self):
        """Отклонение объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="pending",
            category=self.category,
        )
        rejected = reject_ad_instance(ad)
        self.assertEqual(rejected.status, "rejected")
