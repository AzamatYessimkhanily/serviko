# servico_project/urls.py

from django.contrib import admin
from django.urls import path, include
# --- НОВЫЕ ИМПОРТЫ ---
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    # Все URL-адреса, начинающиеся с '', будут искаться в файле directory.urls
    path('', include('directory.urls')), 
]

# --- НОВАЯ СТРОКА ДЛЯ РАЗДАЧИ МЕДИА-ФАЙЛОВ В РЕЖИМЕ РАЗРАБОТКИ ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)