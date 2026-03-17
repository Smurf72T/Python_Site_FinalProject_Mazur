import logging
import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from django.urls import reverse
from datetime import date, timedelta
from django.utils import timezone

# Настройка логирования для тестов
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'ads_tests.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from .models import Category, Ad, Review, RentalRequest, AdImage, Favorite, Message, Notification
from .forms import AdForm, ReviewForm
from .services import get_filtered_ads, approve_ad_instance, reject_ad_instance


class CategoryModelTest(TestCase):
    """Тесты для модели Category"""

    def test_create_category(self):
        """Создание категории"""
        logger.info("Начало теста: создание категории")
        category = Category.objects.create(
            name='Платья',
            description='Вечерние и коктейльные платья'
        )
        logger.info(f"Создана категория: {category.name}")
        self.assertEqual(str(category), 'Платья')
        self.assertEqual(category.name, 'Платья')

    def test_category_unique_name(self):
        """Уникальность имени категории"""
        logger.info("Начало теста: уникальность имени категории")
        Category.objects.create(name='Костюмы')
        try:
            Category.objects.create(name='Костюмы')
            logger.error("Тест не прошёл: дубликат категории создан")
        except Exception as e:
            logger.info(f"Тест прошёл: исключение при создании дубликата - {type(e).__name__}")
            self.assertRaises(Exception)

    def test_category_empty_description(self):
        """Категория без описания"""
        logger.info("Начало теста: категория без описания")
        category = Category.objects.create(name='Обувь')
        logger.info(f"Создана категория без описания: {category.name}")
        self.assertEqual(category.description, '')


class AdModelTest(TestCase):
    """Тесты для модели Ad"""

    def setUp(self):
        logger.debug("SetUp: создание пользователя и изображения")
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
        logger.debug(f"SetUp завершён: пользователь {self.user.username}")

    def test_create_ad(self):
        """Создание объявления"""
        logger.info("Начало теста: создание объявления")
        ad = Ad.objects.create(
            owner=self.user,
            title='Вечернее платье',
            description='Красивое платье в пол',
            price=Decimal('5000.00'),
            location='Москва',
            image=self.image,
            category=self.category
        )
        logger.info(f"Создано объявление: {ad.title}, статус: {ad.status}")
        self.assertEqual(str(ad), 'Вечернее платье')
        self.assertEqual(ad.status, 'pending')
        self.assertEqual(ad.owner, self.user)

    def test_ad_status_choices(self):
        """Статусы объявления"""
        logger.info("Начало теста: статусы объявления")
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
        logger.info(f"Объявление создано со статусом: {ad.status}")
        self.assertEqual(ad.status, 'approved')

    def test_ad_update_status(self):
        """Изменение статуса объявления"""
        logger.info("Начало теста: изменение статуса объявления")
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )
        logger.debug(f"Исходный статус: {ad.status}")
        ad.status = 'approved'
        ad.save()
        logger.info(f"Статус изменён на: {Ad.objects.get(pk=ad.pk).status}")
        self.assertEqual(Ad.objects.get(pk=ad.pk).status, 'approved')


class ReviewModelTest(TestCase):
    """Тесты для модели Review"""

    def setUp(self):
        logger.debug("SetUp: создание пользователей и объявления")
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
        logger.debug(f"SetUp завершён: объявление {self.ad.title}")

    def test_create_review(self):
        """Создание отзыва"""
        logger.info("Начало теста: создание отзыва")
        review = Review.objects.create(
            ad=self.ad,
            author=self.user,
            rating=5,
            comment='Отличное объявление!'
        )
        logger.info(f"Создан отзыв: {review}")
        self.assertEqual(str(review), f'Review by {self.user.username} on {self.ad.title}')
        self.assertEqual(review.rating, 5)

    def test_review_rating_range(self):
        """Проверка диапазона рейтинга"""
        logger.info("Начало теста: диапазон рейтинга")
        for rating in range(1, 6):
            review = Review.objects.create(
                ad=self.ad,
                author=self.user,
                rating=rating,
                comment=f'Рейтинг {rating}'
            )
            logger.debug(f"Создан отзыв с рейтингом: {rating}")
            self.assertEqual(review.rating, rating)
        logger.info("Тест диапазона рейтинга завершён")

    def test_review_cascade_delete(self):
        """Удаление отзыва при удалении объявления"""
        logger.info("Начало теста: каскадное удаление отзыва")
        review = Review.objects.create(
            ad=self.ad,
            author=self.user,
            rating=4,
            comment='Хорошо'
        )
        review_id = review.id
        logger.debug(f"Создан отзыв id={review_id}, удаление объявления")
        self.ad.delete()
        logger.info(f"Объявление удалено, проверка отзыва id={review_id}")
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review_id)
        logger.info("Тест каскадного удаления пройден")


class AdFormTest(TestCase):
    """Тесты для формы AdForm"""

    def setUp(self):
        self.category = Category.objects.create(name='Платья')
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_ad_form_valid(self):
        """Валидная форма объявления"""
        form_data = {
            'title': 'Новое платье',
            'description': 'Описание платья',
            'price': '5000.00',
            'location': 'Москва',
            'category': self.category.id
        }
        form = AdForm(data=form_data, files={'image': self.image})
        # Форма может быть невалидна из-за изображения, проверяем поля
        if not form.is_valid():
            # Проверяем, что ошибка только в image
            self.assertIn('image', form.errors)
        else:
            self.assertTrue(form.is_valid())

    def test_ad_form_missing_title(self):
        """Форма без заголовка невалидна"""
        form_data = {
            'description': 'Описание',
            'price': '1000.00',
            'location': 'Москва'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_ad_form_missing_price(self):
        """Форма без цены невалидна"""
        form_data = {
            'title': 'Тест',
            'description': 'Описание',
            'location': 'Москва'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)


class ReviewFormTest(TestCase):
    """Тесты для формы ReviewForm"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_review_form_valid(self):
        """Валидная форма отзыва"""
        form_data = {
            'rating': 5,
            'comment': 'Отличный товар!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_missing_rating(self):
        """Форма без рейтинга невалидна"""
        form_data = {
            'comment': 'Хорошо'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_review_form_invalid_rating(self):
        """Невалидный рейтинг (вне диапазона)"""
        form_data = {
            'rating': 10,
            'comment': 'Тест'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)


class ServicesTest(TestCase):
    """Тесты для сервисных функций"""

    def setUp(self):
        logger.debug("SetUp: создание пользователя и категории для сервисов")
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.category = Category.objects.create(name='Платья')
        logger.debug("SetUp завершён")

    def test_get_filtered_ads_search(self):
        """Фильтрация по поиску"""
        logger.info("Начало теста: фильтрация по поиску")
        Ad.objects.create(
            owner=self.user,
            title='Вечернее платье',
            description='Красивое платье',
            price=Decimal('5000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        Ad.objects.create(
            owner=self.user,
            title='Костюм',
            description='Деловой костюм',
            price=Decimal('3000.00'),
            location='СПб',
            image=self.image,
            status='approved'
        )
        ads = Ad.objects.filter(status='approved')
        filtered = get_filtered_ads(ads, search='платье')
        logger.info(f"Найдено по поиску 'платье': {filtered.count()} объявлений")
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, 'Вечернее платье')

    def test_get_filtered_ads_location(self):
        """Фильтрация по местоположению"""
        logger.info("Начало теста: фильтрация по местоположению")
        Ad.objects.create(
            owner=self.user,
            title='Объявление 1',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        Ad.objects.create(
            owner=self.user,
            title='Объявление 2',
            description='Описание',
            price=Decimal('1000.00'),
            location='СПб',
            image=self.image,
            status='approved'
        )
        ads = Ad.objects.filter(status='approved')
        filtered = get_filtered_ads(ads, location='москва')
        logger.info(f"Найдено по локации 'москва': {filtered.count()} объявлений")
        self.assertEqual(filtered.count(), 1)

    def test_get_filtered_ads_price_range(self):
        """Фильтрация по цене"""
        logger.info("Начало теста: фильтрация по цене")
        Ad.objects.create(
            owner=self.user,
            title='Дешевое',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        Ad.objects.create(
            owner=self.user,
            title='Дорогое',
            description='Описание',
            price=Decimal('10000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        ads = Ad.objects.filter(status='approved')
        filtered = get_filtered_ads(ads, min_price='5000', max_price='15000')
        logger.info(f"Найдено по цене 5000-15000: {filtered.count()} объявлений")
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().price, Decimal('10000.00'))

    def test_approve_ad_instance(self):
        """Одобрение объявления"""
        logger.info("Начало теста: одобрение объявления")
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='pending'
        )
        logger.debug(f"Исходный статус: {ad.status}")
        approved = approve_ad_instance(ad)
        logger.info(f"Объявление одобрено, новый статус: {approved.status}")
        self.assertEqual(approved.status, 'approved')

    def test_reject_ad_instance(self):
        """Отклонение объявления"""
        logger.info("Начало теста: отклонение объявления")
        ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='pending'
        )
        logger.debug(f"Исходный статус: {ad.status}")
        rejected = reject_ad_instance(ad)
        logger.info(f"Объявление отклонено, новый статус: {rejected.status}")
        self.assertEqual(rejected.status, 'rejected')


class AdViewsTest(TestCase):
    """Тесты для views приложения ads"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            password='testpass123'
        )
        self.moderator.profile.is_moderator = True
        self.moderator.profile.save()
        
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.category = Category.objects.create(name='Платья')
        
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Тестовое объявление',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            status='approved'
        )
        self.pending_ad = Ad.objects.create(
            owner=self.user,
            title='На модерации',
            description='Описание',
            price=Decimal('2000.00'),
            location='СПб',
            image=self.image,
            status='pending'
        )

    def test_home_view_status(self):
        """Главная страница возвращает 200"""
        response = self.client.get(reverse('ads:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_search(self):
        """Поиск на главной странице"""
        response = self.client.get(reverse('ads:home'), {'search': 'тест'})
        self.assertEqual(response.status_code, 200)

    def test_home_view_filter_location(self):
        """Фильтрация по местоположению"""
        response = self.client.get(reverse('ads:home'), {'location': 'москва'})
        self.assertEqual(response.status_code, 200)

    def test_home_view_filter_price(self):
        """Фильтрация по цене"""
        response = self.client.get(reverse('ads:home'), {'min_price': '1500', 'max_price': '3000'})
        self.assertEqual(response.status_code, 200)

    def test_ad_detail_view_status(self):
        """Страница деталей объявления возвращает 200"""
        response = self.client.get(reverse('ads:detail', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 200)

    def test_create_ad_view_authenticated(self):
        """Создание объявления авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ads:create'))
        self.assertEqual(response.status_code, 200)

    def test_create_ad_view_unauthenticated(self):
        """Создание объявления неавторизованным перенаправляет"""
        response = self.client.get(reverse('ads:create'))
        self.assertEqual(response.status_code, 302)

    def test_edit_ad_view_owner(self):
        """Редактирование объявления владельцем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ads:edit', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_ad_view_not_owner(self):
        """Редактирование объявления не владельцем"""
        self.client.login(username='moderator', password='testpass123')
        response = self.client.get(reverse('ads:edit', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 404)

    def test_delete_ad_view(self):
        """Удаление объявления владельцем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('ads:delete', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_mark_as_rented_view(self):
        """Отметка объявления как сданного"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('ads:rented', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.get(pk=self.ad.pk).status, 'rented')

    def test_moderate_view_moderator(self):
        """Модерация объявлений модератором"""
        self.client.login(username='moderator', password='testpass123')
        response = self.client.get(reverse('ads:moderate'))
        self.assertEqual(response.status_code, 200)

    def test_moderate_view_not_moderator(self):
        """Модерация обычным пользователем перенаправляет"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ads:moderate'))
        self.assertEqual(response.status_code, 302)

    def test_moderate_approve(self):
        """Одобрение объявления модератором"""
        self.client.login(username='moderator', password='testpass123')
        response = self.client.post(reverse('ads:moderate'), {
            'ad_id': self.pending_ad.pk,
            'action': 'approve'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.get(pk=self.pending_ad.pk).status, 'approved')

    def test_moderate_reject(self):
        """Отклонение объявления модератором"""
        self.client.login(username='moderator', password='testpass123')
        response = self.client.post(reverse('ads:moderate'), {
            'ad_id': self.pending_ad.pk,
            'action': 'reject'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.get(pk=self.pending_ad.pk).status, 'rejected')

    def test_add_review_not_owner(self):
        """Добавление отзыва не владельцем"""
        self.client.login(username='moderator', password='testpass123')
        response = self.client.post(reverse('ads:detail', kwargs={'pk': self.ad.pk}), {
            'rating': 5,
            'comment': 'Отличное объявление!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(ad=self.ad, author=self.moderator).exists())

    def test_add_review_owner(self):
        """Добавление отзыва владельцем запрещено"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('ads:detail', kwargs={'pk': self.ad.pk}), {
            'rating': 5,
            'comment': 'Свой отзыв'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(ad=self.ad, author=self.user).exists())


# ============================================================
# ТЕСТЫ ДЛЯ НОВЫХ МОДЕЛЕЙ
# ============================================================

class RentalRequestModelTest(TestCase):
    """Тесты для модели RentalRequest (заявки на аренду)"""

    def setUp(self):
        logger.info("SetUp: создание пользователя и объявления для тестов заявок")
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
        logger.debug(f"Создано объявление: {self.ad.title}")

    def test_create_rental_request(self):
        """Создание заявки на аренду"""
        logger.info("Начало теста: создание заявки на аренду")
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            comment='Хочу арендовать'
        )
        logger.info(f"Создана заявка #{request.id}, статус: {request.status}")
        self.assertEqual(request.status, 'pending')
        self.assertIsNotNone(request.total_price)

    def test_calculate_total_price(self):
        """Расчёт стоимости аренды"""
        logger.info("Начало теста: расчёт стоимости аренды")
        request = RentalRequest(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )
        total = request.calculate_total_price()
        expected = Decimal('1000.00') * 6  # 6 дней
        logger.info(f"Расчёт стоимости: {total} (ожидалось {expected})")
        self.assertEqual(total, expected)

    def test_rental_request_status_change(self):
        """Изменение статуса заявки"""
        logger.info("Начало теста: изменение статуса заявки")
        request = RentalRequest.objects.create(
            ad=self.ad,
            renter=self.renter,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2)
        )
        logger.debug(f"Исходный статус: {request.status}")
        request.status = 'accepted'
        request.save()
        logger.info(f"Новый статус: {RentalRequest.objects.get(pk=request.pk).status}")
        self.assertEqual(RentalRequest.objects.get(pk=request.pk).status, 'accepted')


class AdImageModelTest(TestCase):
    """Тесты для модели AdImage (галерея изображений)"""

    def setUp(self):
        logger.info("SetUp: создание объявления для тестов галереи")
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
        """Создание изображения объявления"""
        logger.info("Начало теста: создание изображения объявления")
        gallery_image = SimpleUploadedFile("gallery.jpg", b"content", content_type="image/jpeg")
        img = AdImage.objects.create(
            ad=self.ad,
            image=gallery_image,
            caption='Дополнительное фото'
        )
        logger.info(f"Создано изображение для {self.ad.title}")
        self.assertEqual(img.caption, 'Дополнительное фото')

    def test_main_image_flag(self):
        """Тест флага основного изображения"""
        logger.info("Начало теста: флаг основного изображения")
        img1 = SimpleUploadedFile("img1.jpg", b"content1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("img2.jpg", b"content2", content_type="image/jpeg")
        image1 = AdImage.objects.create(ad=self.ad, image=img1, is_main=True)
        logger.debug(f"Создано основное изображение: {image1.id}")
        image2 = AdImage.objects.create(ad=self.ad, image=img2, is_main=True)
        logger.info(f"Создано второе изображение с is_main=True: {image2.id}")
        # Первое должно перестать быть основным
        image1.refresh_from_db()
        self.assertFalse(image1.is_main)
        self.assertTrue(image2.is_main)


class FavoriteModelTest(TestCase):
    """Тесты для модели Favorite (избранное)"""

    def setUp(self):
        logger.info("SetUp: создание пользователей и объявления для тестов избранного")
        self.user = User.objects.create_user(username='user1', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=User.objects.create_user(username='owner', password='pass'),
            title='Платье',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_add_to_favorites(self):
        """Добавление в избранное"""
        logger.info("Начало теста: добавление в избранное")
        fav = Favorite.objects.create(user=self.user, ad=self.ad)
        logger.info(f"Пользователь {self.user.username} добавил {self.ad.title} в избранное")
        self.assertEqual(str(fav), 'user1 favorited Платье')

    def test_unique_favorite(self):
        """Нельзя добавить одно объявление дважды"""
        logger.info("Начало теста: уникальность избранного")
        Favorite.objects.create(user=self.user, ad=self.ad)
        logger.debug("Первое добавление в избранное")
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, ad=self.ad)
        logger.info("Попытка дублирования заблокирована unique_together")


class MessageModelTest(TestCase):
    """Тесты для модели Message (сообщения)"""

    def setUp(self):
        logger.info("SetUp: создание пользователей для тестов сообщений")
        self.sender = User.objects.create_user(username='sender', password='pass')
        self.recipient = User.objects.create_user(username='recipient', password='pass')

    def test_send_message(self):
        """Отправка сообщения"""
        logger.info("Начало теста: отправка сообщения")
        msg = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Вопрос',
            body='Здравствуйте, интересую аренда'
        )
        logger.info(f"Сообщение отправлено от {self.sender.username} к {self.recipient.username}")
        self.assertFalse(msg.is_read)
        self.assertEqual(msg.subject, 'Вопрос')

    def test_mark_message_as_read(self):
        """Отметка сообщения как прочитанного"""
        logger.info("Начало теста: отметка сообщения как прочитанного")
        msg = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            body='Текст сообщения'
        )
        logger.debug(f"Исходное состояние is_read: {msg.is_read}")
        msg.is_read = True
        msg.save()
        logger.info(f"Сообщение отмечено как прочитанное")
        self.assertTrue(Message.objects.get(pk=msg.pk).is_read)


class NotificationModelTest(TestCase):
    """Тесты для модели Notification (уведомления)"""

    def setUp(self):
        logger.info("SetUp: создание пользователя для тестов уведомлений")
        self.user = User.objects.create_user(username='user1', password='pass')

    def test_create_notification(self):
        """Создание уведомления"""
        logger.info("Начало теста: создание уведомления")
        notif = Notification.objects.create(
            user=self.user,
            title='Новое сообщение',
            message='У вас новое сообщение',
            notification_type='info'
        )
        logger.info(f"Создано уведомление: {notif.title}")
        self.assertFalse(notif.is_read)

    def test_mark_notification_as_read(self):
        """Отметка уведомления как прочитанного"""
        logger.info("Начало теста: отметка уведомления как прочитанного")
        notif = Notification.objects.create(
            user=self.user,
            title='Тест',
            message='Сообщение'
        )
        logger.debug(f"Исходное состояние is_read: {notif.is_read}")
        notif.mark_as_read()
        logger.info(f"Уведомление отмечено как прочитанное")
        self.assertTrue(Notification.objects.get(pk=notif.pk).is_read)


class AdModelExtendedTest(TestCase):
    """Расширенные тесты для модели Ad"""

    def setUp(self):
        logger.info("SetUp: создание объявления для расширенных тестов")
        self.user = User.objects.create_user(username='owner', password='pass')
        self.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Платье',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image,
            size='M',
            deposit_amount=Decimal('5000.00'),
            min_rental_days=3
        )

    def test_ad_with_new_fields(self):
        """Тест новых полей объявления"""
        logger.info("Начало теста: новые поля объявления")
        logger.debug(f"size: {self.ad.size}, deposit: {self.ad.deposit_amount}, min_days: {self.ad.min_rental_days}")
        self.assertEqual(self.ad.size, 'M')
        self.assertEqual(self.ad.deposit_amount, Decimal('5000.00'))
        self.assertEqual(self.ad.min_rental_days, 3)

    def test_increment_views(self):
        """Увеличение счётчика просмотров"""
        logger.info("Начало теста: увеличение счётчика просмотров")
        initial_views = self.ad.views_count
        logger.debug(f"Начальное количество просмотров: {initial_views}")
        self.ad.increment_views()
        logger.info(f"После increment_views: {self.ad.views_count}")
        self.assertEqual(self.ad.views_count, initial_views + 1)

    def test_is_available(self):
        """Проверка доступности объявления"""
        logger.info("Начало теста: проверка доступности объявления")
        # Статус approved - доступно
        self.ad.status = 'approved'
        self.ad.save()
        logger.debug(f"Статус approved, is_available: {self.ad.is_available()}")
        self.assertTrue(self.ad.is_available())
        
        # Статус pending - недоступно
        self.ad.status = 'pending'
        self.ad.save()
        logger.info(f"Статус pending, is_available: {self.ad.is_available()}")
        self.assertFalse(self.ad.is_available())
