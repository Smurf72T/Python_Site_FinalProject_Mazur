"""
Тесты для моделей приложения ads.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.ads.models import (Ad, AdImage, Category, City, Favorite, Message,
                             Notification, RentalRequest, Review)


class CategoryModelTest(TestCase):
    """Тесты для модели Category."""

    def test_create_category(self):
        """Создание категории."""
        category = Category.objects.create(
            name="Платья", description="Вечерние и коктейльные платья"
        )
        self.assertEqual(str(category), "Платья")
        self.assertEqual(category.name, "Платья")

    def test_category_unique_name(self):
        """Уникальность имени категории."""
        Category.objects.create(name="Костюмы")
        with self.assertRaises(Exception):
            Category.objects.create(name="Костюмы")

    def test_category_empty_description(self):
        """Категория без описания."""
        category = Category.objects.create(name="Обувь")
        self.assertEqual(category.description, "")


class CityModelTest(TestCase):
    """Тесты для модели City."""

    def test_create_city(self):
        """Создание города."""
        city = City.objects.create(name="Москва", region="Московская область")
        self.assertEqual(str(city), "Москва (Московская область)")
        self.assertEqual(city.name, "Москва")

    def test_create_city_without_region(self):
        """Город без региона."""
        city = City.objects.create(name="Санкт-Петербург")
        self.assertEqual(str(city), "Санкт-Петербург")
        self.assertEqual(city.region, "")

    def test_city_is_active_default(self):
        """Город активен по умолчанию."""
        city = City.objects.create(name="Казань")
        self.assertTrue(city.is_active)

    def test_city_unique_together(self):
        """Уникальность пары название-регион."""
        City.objects.create(name="Москва", region="Московская область")
        with self.assertRaises(Exception):
            City.objects.create(name="Москва", region="Московская область")

    def test_city_inactive(self):
        """Неактивный город."""
        city = City.objects.create(
            name="Закрытый город", region="Область", is_active=False
        )
        self.assertFalse(city.is_active)


class AdModelTest(TestCase):
    """Тесты для модели Ad."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = Category.objects.create(name="Платья")
        self.city = City.objects.create(name="Москва")
        self.image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )

    def test_create_ad(self):
        """Создание объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Вечернее платье",
            description="Красивое платье в пол",
            price=Decimal("5000.00"),
            deposit_amount=Decimal("10000.00"),
            city=self.city,
            location="Москва, центр",
            image=self.image,
            category=self.category,
            size="M",
            min_rental_days=3,
        )
        self.assertEqual(str(ad), "Вечернее платье")
        self.assertEqual(ad.status, "pending")
        self.assertEqual(ad.owner, self.user)
        self.assertEqual(ad.deposit_amount, Decimal("10000.00"))
        self.assertEqual(ad.city, self.city)
        self.assertEqual(ad.size, "M")
        self.assertEqual(ad.min_rental_days, 3)

    def test_ads_count_updates_on_create_delete(self):
        """Счётчик объявлений в профиле обновляется при создании/удалении."""
        self.assertEqual(self.user.profile.ads_count, 0)

        ad = Ad.objects.create(
            owner=self.user,
            title="Объявление 1",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=self.category,
        )
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.ads_count, 1)

        ad.delete()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.ads_count, 0)

    def test_ads_count_updates_on_owner_change(self):
        """Смена владельца переносит счётчик между профилями."""
        other = User.objects.create_user(
            username="other", password="testpass123"
        )
        ad = Ad.objects.create(
            owner=self.user,
            title="Объявление 1",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=self.category,
        )
        ad.owner = other
        ad.save()
        self.user.profile.refresh_from_db()
        other.profile.refresh_from_db()
        self.assertEqual(self.user.profile.ads_count, 0)
        self.assertEqual(other.profile.ads_count, 1)

    def test_ad_status_choices(self):
        """Статусы объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="СПб",
            image=self.image,
            category=self.category,
            status="approved",
        )
        self.assertEqual(ad.status, "approved")

    def test_ad_update_status(self):
        """Изменение статуса объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
        )
        ad.status = "approved"
        ad.save()
        self.assertEqual(Ad.objects.get(pk=ad.pk).status, "approved")

    def test_is_available_approved(self):
        """Доступность опубликованного объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
        )
        self.assertTrue(ad.is_available())

    def test_is_available_pending(self):
        """Недоступность объявления на модерации."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="pending",
        )
        self.assertFalse(ad.is_available())

    def test_is_available_rented(self):
        """Недоступность сданного объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="rented",
        )
        self.assertFalse(ad.is_available())

    def test_is_available_expired(self):
        """Недоступность объявления с истёкшим сроком аренды."""
        from datetime import date, timedelta

        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
            rental_end_date=date.today() - timedelta(days=1),
        )
        self.assertFalse(ad.is_available())

    def test_increment_views(self):
        """Увеличение счётчика просмотров."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            status="approved",
        )
        initial_views = ad.views_count
        ad.increment_views()
        self.assertEqual(Ad.objects.get(pk=ad.pk).views_count, initial_views + 1)

    def test_ad_size_choices(self):
        """Тест размеров объявления."""
        for size_code, size_label in Ad.SIZE_CHOICES:
            ad = Ad.objects.create(
                owner=self.user,
                title=f"Платье размер {size_code}",
                description="Описание",
                price=Decimal("1000.00"),
                location="Москва",
                image=self.image,
                size=size_code,
                category=self.category,
            )
            self.assertEqual(ad.size, size_code)

    def test_ad_timestamps(self):
        """Тест временных меток."""
        ad = Ad.objects.create(
            owner=self.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=self.category,
        )
        self.assertIsNotNone(ad.created_at)
        self.assertIsNotNone(ad.updated_at)

    def test_ad_rental_dates(self):
        """Тест дат аренды."""
        from datetime import date, timedelta

        start_date = date.today()
        end_date = start_date + timedelta(days=5)

        ad = Ad.objects.create(
            owner=self.user,
            title="Платье на неделю",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=self.category,
            rental_start_date=start_date,
            rental_end_date=end_date,
        )
        self.assertEqual(ad.rental_start_date, start_date)
        self.assertEqual(ad.rental_end_date, end_date)


class ReviewModelTest(TestCase):
    """Тесты для модели Review."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewer", password="testpass123"
        )
        self.owner = User.objects.create_user(username="owner", password="testpass123")
        self.image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.owner,
            title="Тестовое объявление",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
        )

    def test_create_review(self):
        """Создание отзыва."""
        review = Review.objects.create(
            ad=self.ad, author=self.user, rating=5, comment="Отличное объявление!"
        )
        self.assertEqual(
            str(review), f"Review by {self.user.username} on {self.ad.title}"
        )
        self.assertEqual(review.rating, 5)

    def test_review_rating_range(self):
        """Проверка диапазона рейтинга."""
        for rating in range(1, 6):
            review = Review.objects.create(
                ad=self.ad, author=self.user, rating=rating, comment=f"Рейтинг {rating}"
            )
            self.assertEqual(review.rating, rating)

    def test_review_cascade_delete(self):
        """Удаление отзыва при удалении объявления."""
        review = Review.objects.create(
            ad=self.ad, author=self.user, rating=4, comment="Хорошо"
        )
        review_id = review.id
        self.ad.delete()
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review_id)


class RentalRequestModelTest(TestCase):
    """Тесты для модели RentalRequest."""

    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass")
        self.renter = User.objects.create_user(username="renter", password="pass")
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.user,
            title="Платье",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            min_rental_days=2,
        )

    def test_create_rental_request(self):
        """Создание заявки на аренду."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            comment="Хочу арендовать",
            total_price=Decimal("4000.00"),
        )
        self.assertEqual(request.status, "pending")
        self.assertEqual(request.total_price, Decimal("4000.00"))

    def test_calculate_total_price(self):
        """Расчёт стоимости аренды."""
        request = RentalRequest(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
        )
        total = request.calculate_total_price()
        expected = Decimal("1000.00") * 6  # 6 дней
        self.assertEqual(total, expected)

    def test_calculate_total_price_min_days(self):
        """Расчёт стоимости с минимальным сроком аренды."""
        request = RentalRequest(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today(),  # 1 день
        )
        total = request.calculate_total_price()
        # min_rental_days=2, но формула берёт max(days, min_rental_days)
        expected = Decimal("1000.00") * 2
        self.assertEqual(total, expected)

    def test_rental_request_status_change(self):
        """Изменение статуса заявки."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            total_price=Decimal("3000.00"),
        )
        request.status = "accepted"
        request.save()
        self.assertEqual(RentalRequest.objects.get(pk=request.pk).status, "accepted")

    def test_rental_days_property(self):
        """Тест свойства rental_days."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=4),
            total_price=Decimal("5000.00"),
        )
        self.assertEqual(request.rental_days, 5)

    def test_rental_request_timestamps(self):
        """Тест временных меток заявки."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            total_price=Decimal("3000.00"),
        )
        self.assertIsNotNone(request.created_at)
        self.assertIsNotNone(request.updated_at)

    def test_rental_request_status_choices(self):
        """Тест статусов заявки."""
        from datetime import timedelta

        base_date = date.today()
        for i, (status_code, status_label) in enumerate(
            RentalRequest.STATUS_CHOICES
        ):
            request = RentalRequest.objects.create(
                ad=self.ad,
                renter=self.renter,
                start_date=base_date + timedelta(days=i * 10),
                end_date=base_date + timedelta(days=i * 10 + 1),
                status=status_code,
                total_price=Decimal("1000.00"),
            )
            self.assertEqual(request.status, status_code)


class AdImageModelTest(TestCase):
    """Тесты для модели AdImage."""

    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass")
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.user,
            title="Платье",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=Category.objects.create(name="Платья"),
        )

    def test_create_ad_image(self):
        """Создание изображения объявления."""
        gallery_image = SimpleUploadedFile(
            "gallery.jpg", b"content", content_type="image/jpeg"
        )
        img = AdImage.objects.create(
            ad=self.ad, image=gallery_image, caption="Дополнительное фото"
        )
        self.assertEqual(img.caption, "Дополнительное фото")

    def test_main_image_flag(self):
        """Тест флага основного изображения."""
        img1 = SimpleUploadedFile("img1.jpg", b"content1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("img2.jpg", b"content2", content_type="image/jpeg")

        image1 = AdImage.objects.create(ad=self.ad, image=img1, is_main=True)
        image2 = AdImage.objects.create(ad=self.ad, image=img2, is_main=False)

        self.assertTrue(AdImage.objects.get(pk=image1.pk).is_main)

        # Делаем второе изображение основным
        image2.is_main = True
        image2.save()

        self.assertTrue(AdImage.objects.get(pk=image2.pk).is_main)
        self.assertFalse(AdImage.objects.get(pk=image1.pk).is_main)

    def test_ad_image_timestamp(self):
        """Тест временной метки изображения."""
        gallery_image = SimpleUploadedFile(
            "gallery.jpg", b"content", content_type="image/jpeg"
        )
        img = AdImage.objects.create(
            ad=self.ad, image=gallery_image, caption="Тест"
        )
        self.assertIsNotNone(img.created_at)

    def test_ad_image_caption_optional(self):
        """Тест необязательного описания."""
        gallery_image = SimpleUploadedFile(
            "gallery.jpg", b"content", content_type="image/jpeg"
        )
        img = AdImage.objects.create(
            ad=self.ad, image=gallery_image
        )
        self.assertEqual(img.caption, "")


class FavoriteModelTest(TestCase):
    """Тесты для модели Favorite."""

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.user,
            title="Платье",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=Category.objects.create(name="Платья"),
        )

    def test_create_favorite(self):
        """Добавление в избранное."""
        favorite = Favorite.objects.create(user=self.user, ad=self.ad)
        self.assertEqual(
            str(favorite), f"{self.user.username} favorited {self.ad.title}"
        )

    def test_favorite_unique_together(self):
        """Уникальность пары пользователь-объявление."""
        Favorite.objects.create(user=self.user, ad=self.ad)
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, ad=self.ad)

    def test_favorite_timestamp(self):
        """Тест временной метки избранного."""
        favorite = Favorite.objects.create(user=self.user, ad=self.ad)
        self.assertIsNotNone(favorite.created_at)

    def test_favorite_related_names(self):
        """Тест связанных имён."""
        favorite = Favorite.objects.create(user=self.user, ad=self.ad)
        self.assertEqual(self.user.favorites.count(), 1)
        self.assertEqual(self.ad.favorited_by.count(), 1)


class MessageModelTest(TestCase):
    """Тесты для модели Message."""

    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.recipient = User.objects.create_user(username="recipient", password="pass")
        self.image = SimpleUploadedFile(
            "test.jpg", b"content", content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.sender,
            title="Платье",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=Category.objects.create(name="Платья"),
        )

    def test_create_message(self):
        """Создание сообщения."""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject="Тест",
            body="Текст сообщения",
        )
        self.assertIn(self.sender.username, str(message))
        self.assertIn(self.recipient.username, str(message))

    def test_message_default_is_read(self):
        """Сообщение по умолчанию не прочитано."""
        message = Message.objects.create(
            sender=self.sender, recipient=self.recipient, body="Текст"
        )
        self.assertFalse(message.is_read)

    def test_message_with_ad(self):
        """Сообщение с привязкой к объявлению."""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            ad=self.ad,
            body="Интересует ваше объявление",
        )
        self.assertEqual(message.ad, self.ad)

    def test_message_timestamps(self):
        """Тест временных меток сообщения."""
        message = Message.objects.create(
            sender=self.sender, recipient=self.recipient, body="Текст"
        )
        self.assertIsNotNone(message.created_at)
        self.assertIsNotNone(message.updated_at)

    def test_message_mark_as_read(self):
        """Отметка сообщения как прочитанное."""
        message = Message.objects.create(
            sender=self.sender, recipient=self.recipient, body="Тест"
        )
        message.is_read = True
        message.save()
        self.assertTrue(Message.objects.get(pk=message.pk).is_read)

    def test_message_subject_optional(self):
        """Тест необязательной темы сообщения."""
        message = Message.objects.create(
            sender=self.sender, recipient=self.recipient, body="Без темы"
        )
        self.assertEqual(message.subject, "")


class NotificationModelTest(TestCase):
    """Тесты для модели Notification."""

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")

    def test_create_notification(self):
        """Создание уведомления."""
        notification = Notification.objects.create(
            user=self.user, title="Тест", message="Сообщение", notification_type="info"
        )
        self.assertIn("info", str(notification))
        self.assertIn(self.user.username, str(notification))

    def test_notification_default_is_read(self):
        """Уведомление по умолчанию не прочитано."""
        notification = Notification.objects.create(
            user=self.user, title="Тест", message="Сообщение"
        )
        self.assertFalse(notification.is_read)

    def test_mark_as_read(self):
        """Отметка уведомления как прочитанное."""
        notification = Notification.objects.create(
            user=self.user, title="Тест", message="Сообщение"
        )
        notification.mark_as_read()
        self.assertTrue(Notification.objects.get(pk=notification.pk).is_read)

    def test_notification_types(self):
        """Тест типов уведомлений."""
        for type_code, type_label in Notification.TYPE_CHOICES:
            notification = Notification.objects.create(
                user=self.user,
                title=f"Уведомление {type_code}",
                message="Тест",
                notification_type=type_code,
            )
            self.assertEqual(notification.notification_type, type_code)

    def test_notification_link_optional(self):
        """Тест необязательной ссылки."""
        notification = Notification.objects.create(
            user=self.user, title="Тест", message="Сообщение"
        )
        self.assertEqual(notification.link, "")

    def test_notification_timestamp(self):
        """Тест временной метки уведомления."""
        notification = Notification.objects.create(
            user=self.user, title="Тест", message="Сообщение"
        )
        self.assertIsNotNone(notification.created_at)

    def test_notification_related_name(self):
        """Тест связанного имени."""
        Notification.objects.create(
            user=self.user, title="Тест", message="Сообщение"
        )
        self.assertEqual(self.user.notifications.count(), 1)
