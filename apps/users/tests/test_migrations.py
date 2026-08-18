"""
Тесты миграций приложения users.
"""

from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class BackfillAdsCountMigrationTest(TransactionTestCase):
    """
    Проверяет, что миграция users.0004_backfill_ads_count
    пересчитывает счётчик объявлений у существующих профилей.
    """

    migrate_from = [
        ("users", "0003_alter_profile_options_alter_profile_is_moderator_and_more"),
        ("ads", "0005_alter_ad_deposit_amount_alter_ad_min_rental_days"),
    ]
    migrate_to = [("users", "0004_backfill_ads_count")]

    def test_backfill_recalculates_ads_count(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        User = old_apps.get_model("auth", "User")
        Profile = old_apps.get_model("users", "Profile")
        Ad = old_apps.get_model("ads", "Ad")

        # Исторические модели не создают профили через сигналы —
        # создаём их вручную
        user1 = User.objects.create(username="owner1")
        user2 = User.objects.create(username="owner2")
        profile1 = Profile.objects.create(user=user1)
        profile2 = Profile.objects.create(user=user2)

        image = SimpleUploadedFile("t.jpg", b"x", content_type="image/jpeg")
        for i in range(3):
            Ad.objects.create(
                owner=user1,
                title=f"Объявление {i}",
                description="Описание",
                price=Decimal("1000.00"),
                location="Москва",
                image=image,
            )
        Ad.objects.create(
            owner=user2,
            title="Объявление",
            description="Описание",
            price=Decimal("2000.00"),
            location="Москва",
            image=image,
        )

        # Имитируем состояние до миграции: счётчики не совпадают
        Profile.objects.filter(pk=profile1.pk).update(ads_count=0)
        Profile.objects.filter(pk=profile2.pk).update(ads_count=99)

        # Применяем миграцию 0004_backfill_ads_count
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)

        new_apps = executor.loader.project_state(self.migrate_to).apps
        ProfileNew = new_apps.get_model("users", "Profile")

        self.assertEqual(
            ProfileNew.objects.get(pk=profile1.pk).ads_count, 3
        )
        self.assertEqual(
            ProfileNew.objects.get(pk=profile2.pk).ads_count, 1
        )