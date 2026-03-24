"""
Тесты для форм приложения ads.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.ads.forms import AdForm, ReviewForm
from apps.ads.models import Category, Ad


class AdFormTest(TestCase):
    """Тесты для формы AdForm."""

    def setUp(self):
        self.category = Category.objects.create(name='Платья')
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_ad_form_valid(self):
        """Валидная форма объявления."""
        form_data = {
            'title': 'Новое платье',
            'description': 'Описание платья',
            'price': '5000.00',
            'location': 'Москва',
            'category': self.category.id
        }
        form = AdForm(data=form_data, files={'image': self.image})
        self.assertTrue(form.is_valid())

    def test_ad_form_missing_title(self):
        """Форма без заголовка невалидна."""
        form_data = {
            'description': 'Описание',
            'price': '1000.00',
            'location': 'Москва'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_ad_form_missing_price(self):
        """Форма без цены невалидна."""
        form_data = {
            'title': 'Тест',
            'description': 'Описание',
            'location': 'Москва'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_ad_form_missing_location(self):
        """Форма без местоположения невалидна."""
        form_data = {
            'title': 'Тест',
            'description': 'Описание',
            'price': '1000.00'
        }
        form = AdForm(data=form_data, files={'image': self.image})
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)


class ReviewFormTest(TestCase):
    """Тесты для формы ReviewForm."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass'
        )
        self.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg"
        )
        self.ad = Ad.objects.create(
            owner=self.user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=self.image
        )

    def test_review_form_valid(self):
        """Валидная форма отзыва."""
        form_data = {
            'rating': 5,
            'comment': 'Отличный товар!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_missing_rating(self):
        """Форма без рейтинга невалидна."""
        form_data = {
            'comment': 'Хорошо'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_review_form_missing_comment(self):
        """Форма без комментария невалидна."""
        form_data = {
            'rating': 5
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_review_form_invalid_rating(self):
        """Невалидный рейтинг (вне диапазона)."""
        form_data = {
            'rating': 10,
            'comment': 'Тест'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
