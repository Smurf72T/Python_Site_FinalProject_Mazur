"""
Модель дополнительного изображения объявления.
"""
from django.db import models


class AdImage(models.Model):
    """
    Дополнительное изображение объявления.

    Позволяет загружать несколько фотографий для одного объявления.
    """
    ad = models.ForeignKey(
        'Ad',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Объявление'
    )
    image = models.ImageField(
        upload_to='ads_images/gallery/',
        verbose_name='Изображение'
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Описание'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Основное фото'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )

    class Meta:
        verbose_name = 'Изображение объявления'
        verbose_name_plural = 'Изображения объявлений'
        ordering = ['-is_main', '-created_at']

    def __str__(self):
        return f"Image for {self.ad.title}"

    def save(self, *args, **kwargs):
        """
        Сохранить изображение.

        Если изображение помечено как основное, автоматически
        снимает флаг is_main с остальных изображений объявления.
        """
        if self.is_main:
            AdImage.objects.filter(ad=self.ad, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
