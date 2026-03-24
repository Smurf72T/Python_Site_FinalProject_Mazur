"""
Модель категории одежды.
"""

from django.db import models


class Category(models.Model):
    """
    Категория одежды для объявлений.

    Используется для группировки объявлений по типам одежды
    (платья, костюмы, обувь и т.д.).

    Attributes:
        name: Название категории (уникальное).
        description: Описание категории (необязательное).
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name
