"""
Модель заявки на аренду.
"""

from django.contrib.auth.models import User
from django.db import models


class RentalRequest(models.Model):
    """
    Заявка на аренду одежды.

    Пользователь может отправить заявку на аренду объявления.
    Заявка проходит статусы от 'pending' до 'completed'.
    """

    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("accepted", "Подтверждено"),
        ("rejected", "Отклонено"),
        ("cancelled", "Отменено"),
        ("completed", "Завершено"),
    ]

    ad = models.ForeignKey(
        "Ad",
        on_delete=models.CASCADE,
        related_name="rental_requests",
        verbose_name="Объявление",
    )
    renter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rental_requests",
        verbose_name="Арендатор",
    )

    # Даты аренды
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")

    # Статус и информация
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Общая стоимость"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Заявка на аренду"
        verbose_name_plural = "Заявки на аренду"
        ordering = ["-created_at"]
        unique_together = ["ad", "renter", "start_date", "end_date"]

    def __str__(self):
        return f"Request #{self.id} - {self.ad.title} ({self.renter.username})"

    def calculate_total_price(self):
        """
        Рассчитать общую стоимость аренды.
        """
        days = (self.end_date - self.start_date).days + 1
        if days < self.ad.min_rental_days:
            days = self.ad.min_rental_days
        return self.ad.price * days

    def save(self, *args, **kwargs):
        """
        Сохранить заявку с автоматическим расчётом стоимости.
        """
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    @property
    def rental_days(self):
        """
        Количество дней аренды (включительно).
        """
        return (self.end_date - self.start_date).days + 1
