from django.contrib import admin
from .models import Ad, Category, Review, RentalRequest, AdImage, Favorite, Message, Notification

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'price', 'views_count', 'created_at')
    list_filter = ('status', 'category', 'size')
    search_fields = ('title', 'description')
    readonly_fields = ('views_count', 'created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('ad', 'author', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'renter', 'status', 'start_date', 'end_date', 'total_price', 'created_at')
    list_filter = ('status',)
    search_fields = ('ad__title', 'renter__username')

@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ('ad', 'is_main', 'caption', 'created_at')
    list_filter = ('is_main',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'created_at')
    search_fields = ('user__username', 'ad__title')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('sender__username', 'recipient__username', 'subject')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'title')