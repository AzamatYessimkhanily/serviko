# servico_project/urls.py

from django.contrib import admin
from django.urls import path, include
# --- НОВЫЕ ИМПОРТЫ ---
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language # Добавляем для смены языка
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('', include('directory.urls')),
    prefix_default_language=True # Это добавит префикс даже для языка по умолчанию (например, /ru/...)
)

# --- НОВАЯ СТРОКА ДЛЯ РАЗДАЧИ МЕДИА-ФАЙЛОВ В РЕЖИМЕ РАЗРАБОТКИ ---
# В продакшене веб-сервер (Nginx/Apache) будет раздавать статику и медиа.
# Эти строки нужны ТОЛЬКО для DEBUG=True.
# В реальном продакшене settings.DEBUG должен быть False,
# и эти строки не будут активны.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)