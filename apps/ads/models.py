"""
Модели приложения объявлений (ads).

Содержит модели для управления объявлениями об аренде одежды,
категориями, отзывами, заявками на аренду и другими связанными объектами.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """
    Категория одежды для объявлений.
    
    Используется для группировки объявлений по типам одежды
    (платья, костюмы, обувь и т.д.).
    
    Attributes:
        name: Название категории (уникальное).
        description: Описание категории (необязательное).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ad(models.Model):
    """
    Объявление об аренде одежды.
    
    Основная модель приложения, представляющая объявление о сдаче
    одежды в аренду. Содержит информацию о владельце, описании,
    цене, датах аренды и статусе.
    
    Attributes:
        owner: Владелец объявления (пользователь).
        title: Заголовок объявления.
        description: Подробное описание.
        price: Стоимость аренды в сутки.
        deposit_amount: Сумма залога.
        location: Местоположение товара.
        image: Основное изображение.
        category: Категория одежды.
        size: Размер одежды.
        status: Статус объявления (на модерации, опубликовано и т.д.).
        rental_start_date: Дата начала аренды.
        rental_end_date: Дата окончания аренды.
        min_rental_days: Минимальный срок аренды.
        views_count: Количество просмотров.
        created_at: Дата создания.
        updated_at: Дата последнего обновления.
    """
    
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Опубликовано'),
        ('rejected', 'Отклонено'),
        ('rented', 'Сдано'),
    ]

    SIZE_CHOICES = [
        ('XS', 'XS (40-42)'),
        ('S', 'S (42-44)'),
        ('M', 'M (44-46)'),
        ('L', 'L (46-48)'),
        ('XL', 'XL (48-50)'),
        ('XXL', 'XXL (50-52)'),
        ('XXXL', 'XXXL (52+)'),
    ]

    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ads',
        verbose_name='Владелец'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена за сутки'
    )
    deposit_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Залог'
    )
    location = models.CharField(max_length=255, verbose_name='Местоположение')
    image = models.ImageField(
        upload_to='ads_images/', 
        verbose_name='Основное фото'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Категория'
    )
    size = models.CharField(
        max_length=10, 
        choices=SIZE_CHOICES, 
        blank=True, 
        null=True,
        verbose_name='Размер'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Статус'
    )
    
    # Даты аренды
    rental_start_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Начало аренды'
    )
    rental_end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Окончание аренды'
    )
    min_rental_days = models.PositiveIntegerField(
        default=1, 
        verbose_name='Мин. срок аренды (дней)'
    )
    
    # Статистика
    views_count = models.PositiveIntegerField(
        default=0, 
        verbose_name='Просмотры'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_available(self):
        """
        Проверить доступность объявления для аренды.
        
        Returns:
            bool: True если объявление доступно, False иначе.
            
        Объявление недоступно если:
        - Статус не 'approved'
        - Дата окончания аренды истекла
        """
        if self.status != 'approved':
            return False
        if self.rental_end_date and self.rental_end_date < timezone.now().date():
            return False
        return True

    def increment_views(self):
        """
        Увеличить счётчик просмотров на единицу.
        
        Используется при каждом просмотре страницы объявления.
        """
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Review(models.Model):
    """
    Отзыв об объявлении.
    
    Пользователи могут оставлять отзывы и оценки к объявлениям.
    Рейтинг влияет на общий рейтинг владельца объявления.
    
    Attributes:
        ad: Объявление, к которому оставлен отзыв.
        author: Автор отзыва (пользователь).
        rating: Оценка от 1 до 5.
        comment: Текст отзыва.
        created_at: Дата создания отзыва.
    """
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name='Объявление'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Рейтинг'
    )
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.author.username} on {self.ad.title}"
    
    def save(self, *args, **kwargs):
        """
        Сохранить отзыв и обновить рейтинг владельца объявления.
        
        При создании нового отзыва автоматически пересчитывается
        средний рейтинг владельца объявления.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ad.owner.profile.update_rating()


# ============================================================
# НОВЫЕ МОДЕЛИ
# ============================================================

class RentalRequest(models.Model):
    """
    Заявка на аренду одежды.
    
    Пользователь может отправить заявку на аренду объявления.
    Заявка проходит статусы от 'pending' до 'completed'.
    
    Attributes:
        ad: Объявление, на которое создана заявка.
        renter: Арендатор (пользователь).
        start_date: Дата начала аренды.
        end_date: Дата окончания аренды.
        status: Статус заявки.
        comment: Комментарий арендатора.
        total_price: Общая стоимость аренды.
        created_at: Дата создания заявки.
        updated_at: Дата обновления заявки.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Подтверждено'),
        ('rejected', 'Отклонено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE, 
        related_name='rental_requests',
        verbose_name='Объявление'
    )
    renter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='rental_requests',
        verbose_name='Арендатор'
    )
    
    # Даты аренды
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    
    # Статус и информация
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Статус'
    )
    comment = models.TextField(
        blank=True, 
        verbose_name='Комментарий'
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Общая стоимость'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заявка на аренду'
        verbose_name_plural = 'Заявки на аренду'
        ordering = ['-created_at']
        unique_together = ['ad', 'renter', 'start_date', 'end_date']

    def __str__(self):
        return f"Request #{self.id} - {self.ad.title} ({self.renter.username})"
    
    def calculate_total_price(self):
        """
        Рассчитать общую стоимость аренды.
        
        Стоимость = цена за сутки × количество дней.
        Если количество дней меньше минимального срока аренды,
        используется минимальный срок.
        
        Returns:
            Decimal: Общая стоимость аренды.
        """
        days = (self.end_date - self.start_date).days + 1
        if days < self.ad.min_rental_days:
            days = self.ad.min_rental_days
        return self.ad.price * days
    
    def save(self, *args, **kwargs):
        """
        Сохранить заявку с автоматическим расчётом стоимости.

        Если total_price не установлена, вычисляется автоматически.
        """
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    @property
    def rental_days(self):
        """
        Количество дней аренды.

        Returns:
            int: Количество дней (включительно).
        """
        return (self.end_date - self.start_date).days + 1


class AdImage(models.Model):
    """
    Дополнительное изображение объявления.
    
    Позволяет загружать несколько фотографий для одного объявления.
    Одно изображение может быть помечено как основное.
    
    Attributes:
        ad: Объявление, к которому относится изображение.
        image: Файл изображения.
        caption: Описание/подпись к изображению.
        is_main: Флаг основного изображения.
        created_at: Дата загрузки.
    """
    ad = models.ForeignKey(
        Ad, 
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


class Favorite(models.Model):
    """
    Избранное объявление.
    
    Пользователи могут добавлять объявления в избранное
    для быстрого доступа.
    
    Attributes:
        user: Пользователь, добавивший в избранное.
        ad: Объявление в избранном.
        created_at: Дата добавления.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites',
        verbose_name='Пользователь'
    )
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE, 
        related_name='favorited_by',
        verbose_name='Объявление'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['-created_at']
        unique_together = ['user', 'ad']

    def __str__(self):
        return f"{self.user.username} favorited {self.ad.title}"


class Message(models.Model):
    """
    Сообщение между пользователями.
    
    Система внутренних сообщений для общения между
    арендатором и владельцем объявления.
    
    Attributes:
        sender: Отправитель сообщения.
        recipient: Получатель сообщения.
        ad: Связанное объявление (необязательно).
        subject: Тема сообщения.
        body: Текст сообщения.
        is_read: Флаг прочтения.
        created_at: Дата отправки.
        updated_at: Дата обновления.
    """
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name='Получатель'
    )
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='messages',
        verbose_name='Объявление'
    )
    
    subject = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Тема'
    )
    body = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(
        default=False, 
        verbose_name='Прочитано'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата отправки'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.body[:50]}"


class Notification(models.Model):
    """
    Уведомление пользователя.
    
    Система уведомлений для информирования пользователей
    о важных событиях (новые сообщения, статусы заявок и т.д.).
    
    Attributes:
        user: Пользователь, получивший уведомление.
        title: Заголовок уведомления.
        message: Текст уведомления.
        notification_type: Тип уведомления (info, warning, success, error).
        is_read: Флаг прочтения.
        link: Ссылка для перехода (необязательно).
        created_at: Дата создания.
    """
    TYPE_CHOICES = [
        ('info', 'Информация'),
        ('warning', 'Предупреждение'),
        ('success', 'Успех'),
        ('error', 'Ошибка'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=200, 
        verbose_name='Заголовок'
    )
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='info',
        verbose_name='Тип'
    )
    is_read = models.BooleanField(
        default=False, 
        verbose_name='Прочитано'
    )
    link = models.CharField(
        max_length=500, 
        blank=True, 
        verbose_name='Ссылка'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-is_read', '-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} for {self.user.username}"
    
    def mark_as_read(self):
        """
        Отметить уведомление как прочитанное.
        
        Устанавливает флаг is_read в True и сохраняет.
        """
        self.is_read = True
        self.save(update_fields=['is_read'])