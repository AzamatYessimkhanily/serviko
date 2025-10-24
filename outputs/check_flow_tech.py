"""
Проверка: почему не находит по первому слову
Запусти: python manage.py shell
"""

from directory.models import Company

print("=" * 70)
print("ДИАГНОСТИКА: Почему не находит по первому слову")
print("=" * 70)

# Найдём компанию "Flow Tech"
companies = Company.objects.filter(name__icontains="tech")
print(f"\nНайдено компаний с 'tech': {companies.count()}")

for company in companies:
    name = company.name
    print(f"\n" + "=" * 70)
    print(f"Компания: '{name}'")
    print(f"Длина названия: {len(name)}")
    print(f"Первые 10 символов (repr): {repr(name[:10])}")
    print(f"Последние 10 символов (repr): {repr(name[-10:])}")
    
    # Проверяем каждый символ
    print(f"\nПосимвольно:")
    for i, char in enumerate(name[:20]):  # Первые 20 символов
        print(f"  [{i}] = '{char}' (код: {ord(char)})")
    
    # Тесты поиска
    print(f"\n" + "-" * 70)
    print("ТЕСТЫ ПОИСКА:")
    print("-" * 70)
    
    test_queries = ["Flow", "flow", "FLOW", "Tech", "tech", "Flow Tech"]
    
    for query in test_queries:
        # Тест 1: icontains
        result1 = Company.objects.filter(name__icontains=query).count()
        
        # Тест 2: Lower() + contains
        from django.db.models.functions import Lower
        result2 = Company.objects.annotate(
            name_lower=Lower('name')
        ).filter(
            name_lower__contains=query.lower()
        ).count()
        
        # Тест 3: Python
        result3 = query.lower() in name.lower()
        
        print(f"\nЗапрос '{query}':")
        print(f"  icontains: {result1} | Lower(): {result2} | Python: {result3}")
    
    # Разбиваем на слова
    words = name.split()
    print(f"\n" + "-" * 70)
    print(f"Слова в названии: {words}")
    print(f"Количество слов: {len(words)}")
    for i, word in enumerate(words):
        print(f"  Слово {i+1}: '{word}' (длина: {len(word)}, repr: {repr(word)})")

print("\n" + "=" * 70)