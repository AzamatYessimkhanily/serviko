# directory/models.py

from django.db import models
from django.contrib.auth.models import User

# --- Модель Категорий (без изменений) ---
class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название категории")
    # Мы удалили поле 'parent' и 'related_name'

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        # Метод __str__ стал намного проще
        return self.name

# --- Основная модель Компании (с новыми полями) ---
class Company(models.Model):
    # [cite_start]Ценовые диапазоны как в ТЗ [cite: 39]

    owner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Владелец (пользователь)"
    )
    name = models.CharField(max_length=255, verbose_name="Название компании")
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name="Логотип")
    description = models.TextField(verbose_name="Полное описание")
    short_description = models.CharField(max_length=255, verbose_name="Краткое описание для карточки")
    categories = models.ManyToManyField(Category, verbose_name="Категории услуг")
    
    # --- НОВЫЕ ПОЛЯ ---
    founding_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Год основания") # [cite: 49, 117]
    service_area = models.CharField(max_length=255, blank=True, verbose_name="Зона обслуживания (город, район)") # [cite: 51, 101]
    tags = models.CharField(max_length=255, blank=True, verbose_name="Теги (через запятую)", help_text="Например: экспресс-ремонт, эко-материалы, гарантия 5 лет") # [cite: 41, 134-137]
    
    # --- Контакты ---
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    email = models.EmailField(verbose_name="Email для заявок")
    website = models.URLField(blank=True, null=True, verbose_name="Веб-сайт")
    
    # [cite_start]--- НОВЫЕ ПОЛЯ (соцсети) [cite: 53, 103] ---
    instagram_url = models.URLField(blank=True, null=True, verbose_name="Instagram URL")
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook URL")
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn URL")
    whatsapp_contact = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp контакт", help_text="Только цифры, например: 77071234567")
    telegram_contact = models.CharField(max_length=100, blank=True, verbose_name="Telegram контакт", help_text="Username без символа @, например: durov")

    address = models.CharField(max_length=255, verbose_name="Адрес офиса")
    working_hours = models.CharField(max_length=100, verbose_name="График работы")
    
    # --- Флаги и статусы ---
    is_verified = models.BooleanField(default=False, verbose_name="Верифицирована")
    is_popular = models.BooleanField(default=False, verbose_name="Популярна")
    has_fast_response = models.BooleanField(default=False, verbose_name="Быстрый ответ")
    accepts_urgent_orders = models.BooleanField(default=False, verbose_name="Принимает срочные заказы") # [cite: 114]
    provides_on_site_visits = models.BooleanField(default=False, verbose_name="Осуществляет выезд на объект") # [cite: 115]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    favorited_by = models.ManyToManyField(
        User, 
        related_name='favorite_companies', 
        blank=True,
        verbose_name="Кем добавлено в избранное"
    )

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

# --- НОВЫЕ МОДЕЛИ ---

# [cite_start]Модель для услуг компании [cite: 54-59, 122-130]
class Service(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='services', verbose_name="Компания")
    name = models.CharField(max_length=255, verbose_name="Название услуги")
    description = models.TextField(blank=True, verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    unit = models.CharField(max_length=50, blank=True, verbose_name="Единица измерения (за час, за м²)")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return f"{self.name} ({self.company.name})"

# [cite_start]Модель для элементов портфолио [cite: 60-62, 107-109]
class PortfolioItem(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='portfolio_items', verbose_name="Компания")
    image = models.ImageField(upload_to='portfolio_images/', verbose_name="Изображение")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание работы")

    class Meta:
        verbose_name = "Элемент портфолио"
        verbose_name_plural = "Портфолио"

    def __str__(self):
        return f"Работа для {self.company.name}"

# [cite_start]Модель для сертификатов и наград [cite: 63-67, 118-121]
class Certificate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='certificates', verbose_name="Компания")
    file = models.FileField(upload_to='certificates/', verbose_name="Файл (фото или PDF)")
    description = models.CharField(max_length=255, verbose_name="Название/описание сертификата")

    class Meta:
        verbose_name = "Сертификат или награда"
        verbose_name_plural = "Сертификаты и награды"

    def __str__(self):
        return f"Сертификат для {self.company.name}"
    
class Application(models.Model):
    """Модель для хранения заявок от пользователей компаниям."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    message = models.TextField(verbose_name="Текст заявки")
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', blank=True, null=True, verbose_name="Прикрепленный файл")

    selected_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Выбранная услуга")
    desired_date = models.DateField(null=True, blank=True, verbose_name="Желаемая дата")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"  # <-- ИСПРАВЛЕНО
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.user.username} для {self.company.name}"

class Review(models.Model):
    """Модель для отзывов и рейтинга компаний."""
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews', verbose_name="Компания")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    comment = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        # Ограничение: один пользователь - один отзыв на компанию
        unique_together = ('company', 'user')

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.company.name}"
    
class UserProfile(models.Model):
    """Расширенная модель пользователя для хранения аватара."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name="Аватар")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"