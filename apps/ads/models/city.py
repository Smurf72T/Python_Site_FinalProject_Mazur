"""
Модель справочника городов.
"""
from django.db import models


class City(models.Model):
    """
    Город для использования в объявлениях и профилях.

    Attributes:
        name: Название города.
        region: Регион/область.
        is_active: Флаг активности (для отображения в списке).
    """

    name = models.CharField(max_length=100, verbose_name="Город")
    region = models.CharField(
        max_length=100, blank=True, verbose_name="Регион/Область"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ["name"]
        unique_together = ["name", "region"]

    def __str__(self):
        if self.region:
            return f"{self.name} ({self.region})"
        return self.name
