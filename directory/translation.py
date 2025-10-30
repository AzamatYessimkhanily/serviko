from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Company, Service, PortfolioItem, Certificate # Убедитесь, что все импортированы
# TranslationOptions для модели Category
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',) # Поле 'name' будет переводиться

# TranslationOptions для модели Company
class CompanyTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'address', 'working_hours', 'service_area', 'tags')    
    # Добавляйте сюда все поля, которые должны быть многоязычными

# TranslationOptions для модели Service
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'price', 'unit')
    # Добавляйте сюда все поля, которые должны быть многоязычными
# TranslationOptions для модели PortfolioItem
class PortfolioItemTranslationOptions(TranslationOptions):
    fields = ('description',) # Поле 'description' будет переводиться

# TranslationOptions для модели Certificate
class CertificateTranslationOptions(TranslationOptions):
    fields = ('description',)
# Зарегистрируйте модели для перевода
translator.register(Category, CategoryTranslationOptions)
translator.register(Company, CompanyTranslationOptions)
translator.register(Service, ServiceTranslationOptions)
translator.register(PortfolioItem, PortfolioItemTranslationOptions)
translator.register(Certificate, CertificateTranslationOptions)