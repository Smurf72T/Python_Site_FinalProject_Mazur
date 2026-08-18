"""
Тесты для форм приложения ads.
"""

from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.ads.forms import AdForm, ReviewForm
from apps.ads.models import Ad, Category, City


def create_test_image():
    """Создать тестовое изображение в формате JPEG."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer


class AdFormTest(TestCase):
    """Тесты для формы AdForm."""

    def setUp(self):
        self.category = Category.objects.create(name="Платья")
        self.image = SimpleUploadedFile(
            "test_image.jpg", create_test_image().read(), content_type="image/jpeg"
        )

    def test_ad_form_valid(self):
        """Валидная форма объявления."""
        form_data = {
            "title": "Новое платье",
            "description": "Описание платья",
            "price": "5000.00",
            "deposit_amount": "10000.00",
            "min_rental_days": 2,
            "location": "Москва",
            "category": self.category.id,
        }
        form = AdForm(data=form_data, files={"image": self.image})
        if not form.is_valid():
            print(f"Ошибки формы: {form.errors}")
        self.assertTrue(form.is_valid())

    def test_ad_form_missing_title(self):
        """Форма без заголовка невалидна."""
        form_data = {
            "description": "Описание",
            "price": "1000.00",
            "location": "Москва",
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_ad_form_missing_price(self):
        """Форма без цены невалидна."""
        form_data = {"title": "Тест", "description": "Описание", "location": "Москва"}
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_ad_form_missing_location(self):
        """Форма без местоположения невалидна."""
        form_data = {"title": "Тест", "description": "Описание", "price": "1000.00"}
        form = AdForm(data=form_data, files={"image": self.image})
        self.assertFalse(form.is_valid())
        self.assertIn("location", form.errors)


class AdFormCityTest(TestCase):
    """Тесты для поля города в форме AdForm."""

    def setUp(self):
        self.category = Category.objects.create(name="Платья")
        self.image = SimpleUploadedFile(
            "test_image.jpg", create_test_image().read(), content_type="image/jpeg"
        )

    def test_typed_city_name_accepted(self):
        """Ввод названия города из datalist проходит валидацию."""
        form = AdForm(
            data={
                "title": "Новое платье",
                "description": "Описание",
                "price": "5000.00",
                "city": "Москва",
                "location": "ЦАО",
                "category": self.category.id,
            },
            files={"image": self.image},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["city"].name, "Москва")

    def test_new_city_name_created(self):
        """Название города, которого нет в базе, создаёт новый город."""
        form = AdForm(
            data={
                "title": "Новое платье",
                "description": "Описание",
                "price": "5000.00",
                "city": "Тюмень",
                "location": "ЦАО",
                "category": self.category.id,
            },
            files={"image": self.image},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["city"].name, "Тюмень")
        self.assertTrue(City.objects.filter(name="Тюмень").exists())

    def test_empty_city_is_optional(self):
        """Пустой город допустим (поле необязательное)."""
        form = AdForm(
            data={
                "title": "Новое платье",
                "description": "Описание",
                "price": "5000.00",
                "location": "ЦАО",
                "category": self.category.id,
            },
            files={"image": self.image},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["city"])

    def test_edit_renders_city_name_not_pk(self):
        """При редактировании поле города показывает название, а не PK."""
        user = User.objects.create_user(username="owner", password="pass")
        city = City.objects.create(name="Москва", region="Москва")
        ad = Ad.objects.create(
            owner=user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=self.category,
            city=city,
        )
        form = AdForm(instance=ad)
        self.assertIn('value="Москва"', str(form["city"]))

    def test_edit_submit_keeps_city(self):
        """Сохранение редактирования с тем же городом не теряет его."""
        user = User.objects.create_user(username="owner", password="pass")
        city = City.objects.create(name="Москва", region="Москва")
        ad = Ad.objects.create(
            owner=user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=self.image,
            category=self.category,
            city=city,
        )
        form = AdForm(
            data={
                "title": "Тест",
                "description": "Описание",
                "price": "1000.00",
                "city": "Москва",
                "location": "Москва",
                "category": self.category.id,
            },
            files={
                "image": SimpleUploadedFile(
                    "test_image.jpg",
                    create_test_image().read(),
                    content_type="image/jpeg",
                )
            },
            instance=ad,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["city"], city)


class ReviewFormTest(TestCase):
    """Тесты для формы ReviewForm."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="pass")
        cls.image = SimpleUploadedFile(
            "test.jpg", create_test_image().read(), content_type="image/jpeg"
        )
        cls.ad = Ad.objects.create(
            owner=cls.user,
            title="Тест",
            description="Описание",
            price=Decimal("1000.00"),
            location="Москва",
            image=cls.image,
        )

    def test_review_form_valid(self):
        """Валидная форма отзыва."""
        form_data = {"rating": 5, "comment": "Отличный товар!"}
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_missing_rating(self):
        """Форма без рейтинга невалидна."""
        form_data = {"comment": "Хорошо"}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_review_form_missing_comment(self):
        """Форма без комментария невалидна."""
        form_data = {"rating": 5}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    def test_review_form_invalid_rating(self):
        """Невалидный рейтинг (вне диапазона)."""
        form_data = {"rating": 10, "comment": "Тест"}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)
