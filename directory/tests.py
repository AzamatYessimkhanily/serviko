# Файл: directory/tests.py

from django.test import TestCase, Client
# --- НОВЫЙ ИМПОРТ ---
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Company, Category, Application, Review

class DirectoryAppTests(TestCase):
    
    def setUp(self):
        """
        Эта функция выполняется перед каждым тестом.
        """
        # --- Пользователи ---
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.staff_user = User.objects.create_user(username='staffuser', password='password123', is_staff=True)
        self.super_user = User.objects.create_superuser(username='superadmin', password='password123', email='admin@test.com')

        # --- ИСПРАВЛЕНИЕ: Выдаем права нашему тестовому сотруднику ---
        # Находим права (permissions), связанные с моделью Company
        content_type = ContentType.objects.get_for_model(Company)
        permission_change = Permission.objects.get(
            codename='change_company',
            content_type=content_type,
        )
        permission_view = Permission.objects.get(
            codename='view_company',
            content_type=content_type,
        )
        # Добавляем эти права пользователю
        self.staff_user.user_permissions.add(permission_change, permission_view)

        # --- Категории ---
        self.cat_it = Category.objects.create(name='IT Услуги')
        self.cat_web = Category.objects.create(name='Веб-разработка', parent=self.cat_it)

        # --- Компании ---
        self.company_a = Company.objects.create(
            name='Web Wizards',
            short_description='Мастера веб-разработки',
            owner=self.staff_user,
            email='wizards@test.com'
        )
        self.company_a.categories.add(self.cat_web)

        self.company_b = Company.objects.create(
            name='Build Masters',
            short_description='Мастера строительства',
            email='builders@test.com'
        )
    
    # --- Остальные тесты остаются без изменений ---
    
    def test_company_model_creation(self):
        self.assertEqual(Company.objects.count(), 2)
        self.assertEqual(str(self.company_a), 'Web Wizards')

    def test_homepage_access(self):
        response = self.client.get(reverse('company-list'))
        self.assertEqual(response.status_code, 200)

    def test_favorite_page_unauthenticated(self):
        response = self.client.get(reverse('favorite-list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('favorite-list')}")

    def test_favorite_page_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('favorite-list'))
        self.assertEqual(response.status_code, 200)

    def test_search_functionality(self):
        print("Запущен тест: test_search_functionality")
        response = self.client.get(reverse('company-list'), {'q': 'Wizards'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Wizards')
        self.assertNotContains(response, 'Build Masters')

    def test_category_filter(self):
        print("Запущен тест: test_category_filter")
        response = self.client.get(reverse('company-list'), {'category': self.cat_it.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Wizards')
        self.assertNotContains(response, 'Build Masters')

    def test_admin_hides_fields_for_staff(self):
        print("Запущен тест: test_admin_hides_fields_for_staff")
        self.client.login(username='staffuser', password='password123')
        admin_url = reverse('admin:directory_company_change', args=(self.company_a.id,))
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Владелец (пользователь)')
        self.assertNotContains(response, 'Особенности')