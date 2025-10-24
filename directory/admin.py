# directory/admin.py

from django.contrib import admin
from .models import *
from django.contrib.auth.models import User # <-- Добавьте этот импорт вверху файла
import copy

# ============================================
# УЛУЧШЕННАЯ АДМИНКА ДЛЯ КАТЕГОРИЙ
# ============================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_count_display')
    search_fields = ('name',)

    def company_count_display(self, obj):
        """Показывает, в скольких компаниях используется эта категория."""
        count = Company.objects.filter(categories=obj).count()
        return f"{count} компаний"
    company_count_display.short_description = 'Количество компаний'



# ============================================
# INLINES ДЛЯ КОМПАНИЙ
# ============================================

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    verbose_name = "Услуга"
    verbose_name_plural = "Услуги"
    fields = ('name', 'description', 'price', 'unit')


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1
    verbose_name = "Элемент портфолио"
    verbose_name_plural = "Портфолио"
    fields = ('image', 'description')


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 1
    verbose_name = "Сертификат"
    verbose_name_plural = "Сертификаты и награды"
    fields = ('file', 'description')


# ============================================
# УЛУЧШЕННАЯ АДМИНКА ДЛЯ КОМПАНИЙ
# ============================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    # ... (все ваши настройки list_display, fieldsets, inlines и т.д. остаются без изменений)
    list_display = ('name', 'owner', 'email', 'phone_number', 'is_verified', 'is_popular', 'created_at')
    list_filter = ('is_verified', 'is_popular', 'categories', 'accepts_urgent_orders')
    search_fields = ('name', 'description', 'email', 'tags')
    filter_horizontal = ('categories',)
    fieldsets = (
        ('Основная информация', {'fields': ('owner', 'name', 'logo', 'short_description', 'description')}),
        ('Категории и теги', {'fields': ('categories', 'tags'), 'description': 'Выберите одну или несколько категорий. Теги вводите через запятую.'}),
        ('Контактная информация', {'fields': ('phone_number', 'email', 'website', 'address', 'working_hours')}),
        ('Социальные сети', {'fields': ('instagram_url', 'facebook_url', 'linkedin_url', 'whatsapp_contact', 'telegram_contact'), 'classes': ('collapse',)}),
        ('Дополнительная информация', {'fields': ('founding_year', 'service_area')}),
        ('Особенности', {'fields': ('is_verified', 'is_popular', 'has_fast_response', 'accepts_urgent_orders', 'provides_on_site_visits')}),
    )
    inlines = [ ServiceInline, PortfolioItemInline, CertificateInline, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # --- ИСПРАВЛЕННЫЙ МЕТОД ---
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        if not request.user.is_superuser:
            # --- ГЛАВНОЕ ИЗМЕНЕНИЕ: Создаем глубокую копию, а не меняем оригинал ---
            fieldsets_list = copy.deepcopy(list(fieldsets))
            
            # Дальнейшая логика остается прежней
            hidden_fieldset_titles = ('Особенности',)
            fieldsets_list = [fs for fs in fieldsets_list if fs[0] not in hidden_fieldset_titles]
            
            for i, (title, options) in enumerate(fieldsets_list):
                if title == 'Основная информация':
                    fields_list = list(options.get('fields', []))
                    if 'owner' in fields_list:
                        fields_list.remove('owner')
                    options['fields'] = tuple(fields_list)
                    fieldsets_list[i] = (title, options)
                    break
            
            return tuple(fieldsets_list)
        
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        return qs.filter(owner=request.user)

    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
  

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'created_at')
    list_filter = ('company', 'created_at')
    search_fields = ('user__username', 'company__name', 'message')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # --- ИЗМЕНЕНИЕ: Ищем не одну, а ВСЕ компании пользователя ---
        user_companies = Company.objects.filter(owner=request.user)
        
        # Если у пользователя есть хотя бы одна компания
        if user_companies.exists():
            # Показываем заявки, которые относятся к ЛЮБОЙ из его компаний
            return qs.filter(company__in=user_companies)
        
        # Если сотрудник не привязан к компании, он не увидит ни одной заявки
        return qs.none()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'company__name', 'comment')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
            
        # --- ИЗМЕНЕНИЕ: Ищем не одну, а ВСЕ компании пользователя ---
        user_companies = Company.objects.filter(owner=request.user)
        
        if user_companies.exists():
            # Показываем отзывы, которые относятся к ЛЮБОЙ из его компаний
            return qs.filter(company__in=user_companies)

        return qs.none()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Файл: directory/admin.py (в конце)

