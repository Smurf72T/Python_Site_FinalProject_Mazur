"""
Тесты для моделей приложения ads.
"""
from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.ads.models import Category, Ad, Review, RentalRequest, AdImage, Favorite, Message, Notification


class CategoryModelTest(TestCase):
    """Тесты для модели Category."""

    def test_create_category(self):
        """Создание категории."""
        category = Category.objects.create(
            name='Платья',
            description='Вечерние и коктейльные платья'
        )
        self.assertEqual(str(category), 'Платья')
        self.assertEqual(category.name, 'Платья')

    def test_category_unique_name(self):
        """Уникальность имени категории."""
        Category.objects.create(name='Костюмы')
        with self.assertRaises(Exception):
            Category.objects.create(name='Костюмы')

    def test_category_empty_description(self):
        """Категория без описания."""
        category = Category.objects.create(name='Обувь')
        self.assertEqual(category.description, '')


class AdModelTest(TestCase):
    """Тесты для модели Ad."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Платья')
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_create_ad(self):
        """Создание объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title='Вечернее платье',
            description='Красивое платье в пол',
            price=Decimal('5000.00'),
            location='Москва',
            image=self.image,
            category=self.category
        )
        self.assertEqual(str(ad), 'Вечернее платье')
        self.assertEqual(ad.status, 'pending')
        self.assertEqual(ad.owner, self.user)

    def test_ad_status_choices(self):
        """Статусы объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title='Тестовое объявление',
            description='Описание',
            price=Decimal('1000.00'),
            location='СПб',
            image=self.image,
            category=self.category,
            status='approved'
        )
        self.assertEqual(ad.status, 'approved')

    def test_ad_update_status(self):
        """Изменение статуса объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )
        ad.status = 'approved'
        ad.save()
        self.assertEqual(Ad.objects.get(pk=ad.pk).status, 'approved')

    def test_is_available_approved(self):
        """Доступность опубликованного объявления."""
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        self.assertTrue(ad.is_available())

    def test_is_available_pending(self):
        """Недоступность объявления на модерации."""
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='pending'
        )
        self.assertFalse(ad.is_available())

    def test_increment_views(self):
        """Увеличение счётчика просмотров."""
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        initial_views = ad.views_count
        ad.increment_views()
        self.assertEqual(Ad.objects.get(pk=ad.pk).views_count, initial_views + 1)


class ReviewModelTest(TestCase):
    """Тесты для модели Review."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            username='owner',
            password='testpass123'
        )
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.owner,
            title='Тестовое объявление',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_create_review(self):
        """Создание отзыва."""
        review = Review.objects.create(
            ad=self.ad,
            author=self.user,
            rating=5,
            comment='Отличное объявление!'
        )
        self.assertEqual(str(review), f'Review by {self.user.username} on {self.ad.title}')
        self.assertEqual(review.rating, 5)

    def test_review_rating_range(self):
        """Проверка диапазона рейтинга."""
        for rating in range(1, 6):
            review = Review.objects.create(
                ad=self.ad,
                author=self.user,
                rating=rating,
                comment=f'Рейтинг {rating}'
            )
            self.assertEqual(review.rating, rating)

    def test_review_cascade_delete(self):
        """Удаление отзыва при удалении объявления."""
        review = Review.objects.create(
            ad=self.ad,
            author=self.user,
            rating=4,
            comment='Хорошо'
        )
        review_id = review.id
        self.ad.delete()
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review_id)


class RentalRequestModelTest(TestCase):
    """Тесты для модели RentalRequest."""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass')
        self.renter = User.objects.create_user(username='renter', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Платье',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_create_rental_request(self):
        """Создание заявки на аренду."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            comment='Хочу арендовать'
        )
        self.assertEqual(request.status, 'pending')
        self.assertIsNotNone(request.total_price)

    def test_calculate_total_price(self):
        """Расчёт стоимости аренды."""
        request = RentalRequest(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )
        total = request.calculate_total_price()
        expected = Decimal('1000.00') * 6  # 6 дней
        self.assertEqual(total, expected)

    def test_rental_request_status_change(self):
        """Изменение статуса заявки."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2)
        )
        request.status = 'accepted'
        request.save()
        self.assertEqual(RentalRequest.objects.get(pk=request.pk).status, 'accepted')

    def test_rental_days_property(self):
        """Тест свойства rental_days."""
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=4)
        )
        self.assertEqual(request.rental_days, 5)


class AdImageModelTest(TestCase):
    """Тесты для модели AdImage."""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Платье',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_create_ad_image(self):
        """Создание изображения объявления."""
        gallery_image = SimpleUploadedFile("gallery.jpg", b"content", content_type="image/jpeg")
        img = AdImage.objects.create(
            ad=self.ad,
            image=gallery_image,
            caption='Дополнительное фото'
        )
        self.assertEqual(img.caption, 'Дополнительное фото')

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


class FavoriteModelTest(TestCase):
    """Тесты для модели Favorite."""

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Платье',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_create_favorite(self):
        """Добавление в избранное."""
        favorite = Favorite.objects.create(user=self.user, ad=self.ad)
        self.assertEqual(str(favorite), f"{self.user.username} favorited {self.ad.title}")

    def test_favorite_unique_together(self):
        """Уникальность пары пользователь-объявление."""
        Favorite.objects.create(user=self.user, ad=self.ad)
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, ad=self.ad)


class MessageModelTest(TestCase):
    """Тесты для модели Message."""

    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='pass')
        self.recipient = User.objects.create_user(username='recipient', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=self.sender,
            title='Платье',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_create_message(self):
        """Создание сообщения."""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Тест',
            body='Текст сообщения'
        )
        self.assertIn(self.sender.username, str(message))
        self.assertIn(self.recipient.username, str(message))

    def test_message_default_is_read(self):
        """Сообщение по умолчанию не прочитано."""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            body='Текст'
        )
        self.assertFalse(message.is_read)


class NotificationModelTest(TestCase):
    """Тесты для модели Notification."""

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')

    def test_create_notification(self):
        """Создание уведомления."""
        notification = Notification.objects.create(
            user=self.user,
            title='Тест',
            message='Сообщение',
            notification_type='info'
        )
        self.assertIn('info', str(notification))
        self.assertIn(self.user.username, str(notification))

    def test_notification_default_is_read(self):
        """Уведомление по умолчанию не прочитано."""
        notification = Notification.objects.create(
            user=self.user,
            title='Тест',
            message='Сообщение'
        )
        self.assertFalse(notification.is_read)

    def test_mark_as_read(self):
        """Отметка уведомления как прочитанное."""
        notification = Notification.objects.create(
            user=self.user,
            title='Тест',
            message='Сообщение'
        )
        notification.mark_as_read()
        self.assertTrue(Notification.objects.get(pk=notification.pk).is_read)
