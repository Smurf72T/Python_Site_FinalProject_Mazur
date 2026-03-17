from django.contrib import admin
from .models import Ad, Category, Review

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')

admin.site.register(Category)
admin.site.register(Review)