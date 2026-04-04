"""
Тесты для context_processors, templatetags и management commands.
"""

from datetime import date
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, RequestFactory
from PIL import Image

from apps.ads.models import Ad, Category, City, Notification
from apps.ads.templatetags.rental_tags import days_between
from apps.ads.context_processors import unread_notifications


def create_test_image():
    """Создать тестовое изображение в формате JPEG."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer


# =============================================================================
# Тесты для context_processors
# =============================================================================


class UnreadNotificationsContextProcessorTest(TestCase):
    """Тесты для контекст-процессора непрочитанных уведомлений."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.factory = RequestFactory()

    def test_unread_count_for_authenticated_user(self):
        """Непрочитанные уведомления для авторизованного пользователя."""
        Notification.objects.create(
            user=self.user,
            title="Тест",
            message="Сообщение",
            notification_type="info",
            is_read=False,
        )
        Notification.objects.create(
            user=self.user,
            title="Тест 2",
            message="Сообщение 2",
            notification_type="info",
            is_read=False,
        )
        request = self.factory.get("/")
        request.user = self.user
        result = unread_notifications(request)
        self.assertEqual(result["unread_count"], 2)

    def test_unread_count_for_authenticated_no_notifications(self):
        """Авторизованный пользователь без уведомлений."""
        request = self.factory.get("/")
        request.user = self.user
        result = unread_notifications(request)
        self.assertEqual(result["unread_count"], 0)

    def test_unread_count_for_anonymous_user(self):
        """Анонимный пользователь — 0 уведомлений."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/")
        request.user = AnonymousUser()
        result = unread_notifications(request)
        self.assertEqual(result["unread_count"], 0)

    def test_unread_count_skips_admin_path(self):
        """Админские запросы пропускаются."""
        request = self.factory.get("/admin/")
        request.user = self.user
        result = unread_notifications(request)
        self.assertEqual(result["unread_count"], 0)

    def test_unread_count_only_unread(self):
        """Считаются только непрочитанные уведомления."""
        Notification.objects.create(
            user=self.user,
            title="Прочитано",
            message="Сообщение",
            notification_type="info",
            is_read=True,
        )
        Notification.objects.create(
            user=self.user,
            title="Не прочитано",
            message="Сообщение",
            notification_type="info",
            is_read=False,
        )
        request = self.factory.get("/")
        request.user = self.user
        result = unread_notifications(request)
        self.assertEqual(result["unread_count"], 1)


# =============================================================================
# Тесты для templatetags
# =============================================================================


class DaysBetweenTemplateTest(TestCase):
    """Тесты для шаблонного фильтра days_between."""

    def test_days_between_valid_dates(self):
        """Вычисление дней между двумя датами."""
        start = date(2026, 4, 1)
        end = date(2026, 4, 5)
        result = days_between(start, end)
        self.assertEqual(result, 5)  # включительно

    def test_days_between_same_day(self):
        """Один и тот же день — 1 день."""
        start = date(2026, 4, 1)
        end = date(2026, 4, 1)
        result = days_between(start, end)
        self.assertEqual(result, 1)

    def test_days_between_end_before_start(self):
        """Дата окончания раньше начала — отрицательное значение."""
        start = date(2026, 4, 10)
        end = date(2026, 4, 1)
        result = days_between(start, end)
        self.assertEqual(result, -8)

    def test_days_between_start_none(self):
        """Начальная дата None — возвращает 0."""
        end = date(2026, 4, 5)
        result = days_between(None, end)
        self.assertEqual(result, 0)

    def test_days_between_end_none(self):
        """Конечная дата None — возвращает 0."""
        start = date(2026, 4, 1)
        result = days_between(start, None)
        self.assertEqual(result, 0)

    def test_days_between_both_none(self):
        """Обе даты None — возвращает 0."""
        result = days_between(None, None)
        self.assertEqual(result, 0)


# =============================================================================
# Тесты для management commands
# =============================================================================


class InitDataCommandTest(TestCase):
    """Тесты для команды init_data."""

    def test_init_data_creates_categories_and_cities(self):
        """Команда создаёт категории и города когда таблицы пусты."""
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(City.objects.count(), 0)

        call_command("init_data")

        self.assertEqual(Category.objects.count(), 15)
        self.assertEqual(City.objects.count(), 10)

    def test_init_data_skips_existing_categories(self):
        """Команда пропускает существующие категории."""
        # Создаём все категории заранее
        for cat_data in [
            {"name": "Платья", "description": "Старое описание"},
        ]:
            Category.objects.create(**cat_data)
        for city_data in [{"name": "Москва", "region": "Москва"}]:
            City.objects.create(**city_data)

        call_command("init_data")

        # Команда не добавляет дубликаты, но и не заполняет недостающие
        # (так как таблица уже не пустая)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(City.objects.count(), 1)

    def test_init_data_partial_categories(self):
        """Команда не дополняет категории если таблица не пустая."""
        # Создаём только одну категорию
        Category.objects.create(name="Платья", description="Платья")
        call_command("init_data")
        # init_data проверяет count() == 0, поэтому не добавляет
        self.assertEqual(Category.objects.count(), 1)


class FillCategoriesCommandTest(TestCase):
    """Тесты для команды fill_categories."""

    def test_fill_categories_creates_all(self):
        """Команда создаёт все категории."""
        call_command("fill_categories")
        self.assertEqual(Category.objects.count(), 15)
        self.assertTrue(Category.objects.filter(name="Платья").exists())
        self.assertTrue(Category.objects.filter(name="Костюмы").exists())
        self.assertTrue(Category.objects.filter(name="Обувь").exists())

    def test_fill_categories_skips_existing(self):
        """Команда пропускает существующие категории."""
        Category.objects.create(name="Платья", description="Моё описание")
        call_command("fill_categories")
        self.assertEqual(Category.objects.count(), 15)
        # Оригинальное описание сохранено
        category = Category.objects.get(name="Платья")
        self.assertEqual(category.description, "Моё описание")

    def test_fill_categories_idempotent(self):
        """Команда идемпотентна — повторный запуск не дублирует."""
        call_command("fill_categories")
        call_command("fill_categories")
        self.assertEqual(Category.objects.count(), 15)


class FillCitiesCommandTest(TestCase):
    """Тесты для команды fill_cities."""

    def test_fill_cities_creates_all(self):
        """Команда создаёт все города."""
        call_command("fill_cities")
        self.assertEqual(City.objects.count(), 10)
        self.assertTrue(City.objects.filter(name="Москва").exists())
        self.assertTrue(City.objects.filter(name="Санкт-Петербург").exists())
        self.assertTrue(City.objects.filter(name="Казань").exists())

    def test_fill_cities_skips_existing(self):
        """Команда пропускает существующие города."""
        City.objects.create(name="Москва", region="Московская область")
        call_command("fill_cities")
        self.assertEqual(City.objects.count(), 10)
        # Оригинальный регион сохранён
        city = City.objects.get(name="Москва")
        self.assertEqual(city.region, "Московская область")

    def test_fill_cities_idempotent(self):
        """Команда идемпотентна — повторный запуск не дублирует."""
        call_command("fill_cities")
        call_command("fill_cities")
        self.assertEqual(City.objects.count(), 10)
