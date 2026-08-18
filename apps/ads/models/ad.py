"""
Модель объявления об аренде одежды.
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.utils import timezone

from .city import City


class Ad(models.Model):
    """
    Объявление об аренде одежды.

    Основная модель приложения, представляющая объявление о сдаче
    одежды в аренду. Содержит информацию о владельце, описании,
    цене, датах аренды и статусе.
    """

    STATUS_CHOICES = [
        ("pending", "На модерации"),
        ("approved", "Опубликовано"),
        ("rejected", "Отклонено"),
        ("rented", "Сдано"),
    ]

    SIZE_CHOICES = [
        ("XS", "XS (40-42)"),
        ("S", "S (42-44)"),
        ("M", "M (44-46)"),
        ("L", "L (46-48)"),
        ("XL", "XL (48-50)"),
        ("XXL", "XXL (50-52)"),
        ("XXXL", "XXXL (52+)"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Владелец",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена за сутки"
    )
    deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True, verbose_name="Залог"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Город",
        help_text="Выберите город из списка или введите свой",
    )
    location = models.CharField(max_length=255, verbose_name="Местоположение")
    image = models.ImageField(
        upload_to="ads_images/", verbose_name="Основное фото"
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Размер",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
    )

    # Даты аренды
    rental_start_date = models.DateField(
        null=True, blank=True, verbose_name="Начало аренды"
    )
    rental_end_date = models.DateField(
        null=True, blank=True, verbose_name="Окончание аренды"
    )
    min_rental_days = models.PositiveIntegerField(
        default=1, blank=True, verbose_name="Мин. срок аренды (дней)"
    )

    # Статистика
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Просмотры"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def is_available(self):
        """
        Проверить доступность объявления для аренды.

        Returns:
            bool: True если объявление доступно, False иначе.
        """
        if self.status != "approved":
            return False
        if (
            self.rental_end_date
            and self.rental_end_date < timezone.now().date()
        ):
            return False
        return True

    def increment_views(self):
        """
        Увеличить счётчик просмотров на единицу (атомарно).
        """
        Ad.objects.filter(pk=self.pk).update(views_count=F("views_count") + 1)
        self.refresh_from_db(fields=["views_count"])

    def save(self, *args, **kwargs):
        """
        Сохранить объявление и обновить счётчик объявлений владельца.
        """
        updating_fields = kwargs.get("update_fields")
        # Счётчик не трогаем при точечных обновлениях (например, просмотры)
        if updating_fields and "owner_id" not in updating_fields:
            super().save(*args, **kwargs)
            return

        is_new = self.pk is None
        old_owner_id = None
        if not is_new:
            old_owner_id = (
                Ad.objects.filter(pk=self.pk)
                .values_list("owner_id", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if is_new:
            self._adjust_ads_count(self.owner_id, 1)
        elif old_owner_id and old_owner_id != self.owner_id:
            self._adjust_ads_count(old_owner_id, -1)
            self._adjust_ads_count(self.owner_id, 1)

    def delete(self, *args, **kwargs):
        """Удалить объявление и уменьшить счётчик объявлений владельца."""
        owner_id = self.owner_id
        super().delete(*args, **kwargs)
        self._adjust_ads_count(owner_id, -1)

    @staticmethod
    def _adjust_ads_count(owner_id, delta):
        """Прибавить delta к счётчику объявлений профиля владельца."""
        from apps.users.models import Profile

        if owner_id:
            Profile.objects.filter(user_id=owner_id).update(
                ads_count=F("ads_count") + delta
            )
