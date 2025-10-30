from django.test import TestCase, Client
from django.urls import reverse
from django.utils import translation # Для принудительной смены языка в тестах

from directory.models import Category, Company, Service, PortfolioItem, Certificate
from django.contrib.auth import get_user_model

User = get_user_model()

class MultiLanguageTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client = Client()

        # Создаем тестовые данные на разных языках
        # Категория
        self.category = Category.objects.create(
            name_ru='Тестовая Категория РУ',
            name_en='Test Category EN',
            name_kk='Сынақ Санат ҚҚ'
        )

        # Компания
        self.company = Company.objects.create(
            owner=self.user,
            name_ru='Тестовая Компания РУ',
            name_en='Test Company EN',
            name_kk='Сынақ Компания ҚҚ',
            short_description_ru='Короткое описание РУ',
            short_description_en='Short description EN',
            short_description_kk='Қысқаша сипаттама ҚҚ',
            description_ru='Полное описание РУ',
            description_en='Full description EN',
            description_kk='Толық сипаттама ҚҚ',
            address_ru='Тестовый адрес РУ',
            address_en='Test address EN',
            address_kk='Сынақ мекенжай ҚҚ',
            working_hours_ru='Пн-Пт 9:00-18:00 РУ',
            working_hours_en='Mon-Fri 9:00-18:00 EN',
            working_hours_kk='Дс-Жм 9:00-18:00 ҚҚ',
            service_area_ru='Тестовая область обслуживания РУ',
            service_area_en='Test service area EN',
            service_area_kk='Сынақ қызмет көрсету аймағы ҚҚ',
            tags_ru='тег1,тег2,тег3 РУ',
            tags_en='tag1,tag2,tag3 EN',
            tags_kk='тег1,тег2,тег3 ҚҚ',
        )
        self.company.categories.add(self.category) # Привязываем категорию

        # Услуга
        self.service = Service.objects.create(
            company=self.company,
            name_ru='Тестовая Услуга РУ',
            name_en='Test Service EN',
            name_kk='Сынақ Қызмет ҚҚ',
            description_ru='Описание услуги РУ',
            description_en='Service description EN',
            description_kk='Қызмет сипаттамасы ҚҚ',
            price=100.00,
            unit_ru='шт.',
            unit_en='pc.',
            unit_kk='дана'
        )

        # Элемент портфолио
        self.portfolio_item = PortfolioItem.objects.create(
            company=self.company,
            description_ru='Описание портфолио РУ',
            description_en='Portfolio description EN',
            description_kk='Портфолио сипаттамасы ҚҚ'
        )

        # Сертификат
        self.certificate = Certificate.objects.create(
            company=self.company,
            description_ru='Описание сертификата РУ',
            description_en='Certificate description EN',
            description_kk='Сертификат сипаттамасы ҚҚ'
        )


    def test_model_translation_fields(self):
        # Проверка прямого доступа к полям
        self.assertEqual(self.category.name_ru, 'Тестовая Категория РУ')
        self.assertEqual(self.category.name_en, 'Test Category EN')
        self.assertEqual(self.category.name_kk, 'Сынақ Санат ҚҚ')

        # Проверка "умного" доступа (получение активного языка)
        with translation.override('ru'):
            self.assertEqual(self.category.name, 'Тестовая Категория РУ')
            self.assertEqual(self.company.name, 'Тестовая Компания РУ')
            self.assertEqual(self.service.name, 'Тестовая Услуга РУ')
        with translation.override('en'):
            self.assertEqual(self.category.name, 'Test Category EN')
            self.assertEqual(self.company.name, 'Test Company EN')
            self.assertEqual(self.service.name, 'Test Service EN')
        with translation.override('kk'):
            self.assertEqual(self.category.name, 'Сынақ Санат ҚҚ')
            self.assertEqual(self.company.name, 'Сынақ Компания ҚҚ')
            self.assertEqual(self.service.name, 'Сынақ Қызмет ҚҚ')

        # Проверка других полей компании
        with translation.override('en'):
            self.assertEqual(self.company.short_description, 'Short description EN')
            self.assertEqual(self.company.description, 'Full description EN')
            self.assertEqual(self.company.address, 'Test address EN')
            self.assertEqual(self.company.working_hours, 'Mon-Fri 9:00-18:00 EN')
            self.assertEqual(self.company.service_area, 'Test service area EN')
            self.assertEqual(self.company.tags, 'tag1,tag2,tag3 EN')
            self.assertEqual(self.service.unit, 'pc.')
            self.assertEqual(self.portfolio_item.description, 'Portfolio description EN')
            self.assertEqual(self.certificate.description, 'Certificate description EN')


    def test_i18n_urls_and_content(self):
        # Проверка URL-ов и контента для списка компаний
        for lang_code, expected_content in [
            ('ru', 'Тестовая Компания РУ'),
            ('en', 'Test Company EN'),
            ('kk', 'Сынақ Компания ҚҚ')
        ]:
            with self.subTest(lang=lang_code):
                url = reverse('company_list') # Assuming 'company_list' is a root URL like /companies/
                # Если у вас есть prefix_default_language=True, то URL будет с префиксом.
                # 'company_list' должен быть определен в directory/urls.py
                # Мы получаем URL без префикса, а Django Client добавит его, если мы установим язык.
                response = self.client.get(f'/{lang_code}{url}') # Явно указываем префикс для клиента
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_content)
                self.assertContains(response, f'<html lang="{lang_code}">') # Проверка, что lang в html теге верный

        # Проверка URL-ов и контента для детальной страницы компании
        for lang_code, expected_content_name, expected_content_description in [
            ('ru', 'Тестовая Компания РУ', 'Полное описание РУ'),
            ('en', 'Test Company EN', 'Full description EN'),
            ('kk', 'Сынақ Компания ҚҚ', 'Толық сипаттама ҚҚ')
        ]:
            with self.subTest(lang=lang_code):
                # Предположим, у вас есть URL-паттерн 'company_detail' с slug
                url = reverse('company_detail', kwargs={'slug': self.company.slug})
                response = self.client.get(f'/{lang_code}{url}') # Явно указываем префикс для клиента
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_content_name)
                self.assertContains(response, expected_content_description)
                self.assertContains(response, f'<html lang="{lang_code}">')


    def test_static_text_translation(self):
        # Предположим, 'company_list' или '/' содержит 'Все права защищены'
        # (убедитесь, что вы пометили эту строку для перевода)
        # Убедитесь, что эти переводы есть в ваших .po файлах и скомпилированы.
        for lang_code, expected_static_text in [
            ('ru', 'Все права защищены'),
            ('en', 'All rights reserved'),
            ('kk', 'Барлық құқықтар қорғалған')
        ]:
            with self.subTest(lang=lang_code):
                # Используем корневой URL, который загружает base.html
                response = self.client.get(f'/{lang_code}/')
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_static_text)


    def test_language_switcher(self):
        # Тестирование переключателя языка
        # Отправляем POST запрос на set_language
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/ru/'}, # next - это куда вернуться
            follow=True # Следовать за редиректом
        )
        self.assertEqual(response.status_code, 200) # Проверяем, что запрос прошел успешно после редиректа
        self.assertContains(response, '<html lang="en">') # Проверяем, что страница теперь на английском
        self.assertRedirects(response, '/en/') # Убедимся, что редирект был на /en/

        response = self.client.post(
            reverse('set_language'),
            {'language': 'kk', 'next': '/en/company/test-company-en/'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="kk">')
        # Важно: URL после редиректа должен быть /kk/company/synaq-kompaniia-qq/
        # То есть slug тоже должен быть переведен, если вы используете MultiLingualSlugField
        # Если slug не переводится, то будет /kk/company/test-company-en/
        # В данном тесте предполагается, что slug не переводится или Company detail View
        # может обрабатывать slug на любом языке.
        # Если slug должен быть переведен, этот тест нужно будет скорректировать.
        self.assertRedirects(response, f'/kk/company/{self.company.slug_kk}/' if hasattr(self.company, 'slug_kk') else f'/kk/company/{self.company.slug}/')