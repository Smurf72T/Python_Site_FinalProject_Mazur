from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Проверка: включать ли URL админки (для контейнера admin)
ENABLE_ADMIN_URL = getattr(settings, "ENABLE_ADMIN_URL", True)

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("", include("apps.ads.urls")),
]

# Админка только если включена (для контейнера admin)
if ENABLE_ADMIN_URL:
    urlpatterns.insert(0, path("admin/", admin.site.urls))

# Отображение медиа-файлов в режиме разработки и для админки
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
