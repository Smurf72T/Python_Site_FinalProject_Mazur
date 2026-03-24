from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.utils.html import format_html

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('', include('apps.ads.urls')),
]

# Отображение медиа-файлов в режиме разработки и для админки
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)