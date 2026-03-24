"""
Базовые настройки и утилиты для тестов приложения ads.
"""
import logging
import os
from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

# Настройка логирования для тестов
LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'logs'
)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'ads_tests.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseAdsTestCase(TestCase):
    """
    Базовый класс для тестов приложения ads.

    Предоставляет общие методы и данные для тестов.
    """

    @classmethod
    def setUpTestData(cls):
        """Создание общих тестовых данных."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def create_category(self, name='Платья', description=''):
        """Создать категорию."""
        from .models import Category
        return Category.objects.create(name=name, description=description)

    def create_ad(self, owner=None, status='pending', **kwargs):
        """Создать объявление."""
        from .models import Ad, Category

        if owner is None:
            owner = self.user

        category = kwargs.pop('category', None)
        if category is None:
            category = self.create_category()

        defaults = {
            'owner': owner,
            'title': 'Тестовое объявление',
            'description': 'Описание',
            'price': Decimal('1000.00'),
            'location': 'Москва',
            'image': self.image,
            'category': category,
            'status': status,
        }
        defaults.update(kwargs)
        return Ad.objects.create(**defaults)

    def create_user(self, username='user', password='pass123', **kwargs):
        """Создать пользователя."""
        defaults = {'password': password}
        defaults.update(kwargs)
        return User.objects.create_user(username=username, **defaults)
