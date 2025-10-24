# directory/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.db.models import Q, Case, When, Value, IntegerField, Count
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PartnershipRequestForm 
from .forms import RequestForm, ReviewForm ,CustomUserCreationForm ,UserUpdateForm, ProfileUpdateForm
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.core.mail import send_mail, EmailMessage
# ... (остальные views без изменений) ...
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
# ... (все ваши импорты)
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Avg, Count # Убедитесь, что Avg импортирован
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator

# Файл: directory/views.py

# Файл: directory/views.py

def company_list_view(request):
    """Финальная версия view для списка компаний со всеми фильтрами и приоритетной сортировкой."""
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'relevance')
    selected_category_ids = request.GET.getlist('category')
    selected_cities = request.GET.getlist('city')
    min_rating_str = request.GET.get('min_rating', '0.0')

    companies_queryset = Company.objects.all().annotate(average_rating=Avg('reviews__rating'))

    # --- Применение всех фильтров (ваш код без изменений) ---
    if selected_category_ids:
        companies_queryset = companies_queryset.filter(categories__id__in=selected_category_ids).distinct()
    if selected_cities:
        q_city = Q()
        for city in selected_cities:
            q_city |= Q(service_area__icontains=city)
        companies_queryset = companies_queryset.filter(q_city)
    try:
        min_rating_val = Decimal(min_rating_str)
        if min_rating_val > 0:
            companies_queryset = companies_queryset.filter(average_rating__gte=min_rating_val)
    except (InvalidOperation, TypeError):
        min_rating_str = '0.0'

    # --- УЛУЧШЕННЫЙ ПОИСК (ваш код без изменений) ---
    if search_query:
        search_terms = search_query.split()
        q_objects = Q()
        for term in search_terms:
            q_objects &= (
                Q(name__icontains=term) | Q(tags__icontains=term) |
                Q(short_description__icontains=term) | Q(description__icontains=term) |
                Q(categories__name__icontains=term) | Q(services__name__icontains=term)
            )
        companies_queryset = companies_queryset.filter(q_objects).distinct()

    # --- ИЗМЕНЕНИЕ: НОВАЯ ЛОГИКА СОРТИРОВКИ ---

    # 1. Задаем базовый приоритет: сначала "популярные", потом "верифицированные"
    primary_sort_order = ['-is_popular', '-is_verified']

    if search_query and (sort_by == 'relevance' or not sort_by):
        # Логика для релевантности (ваш код)
        relevance_conditions = []
        for i, term in enumerate(search_terms, start=1):
            relevance_conditions.extend([
                When(name__iexact=term, then=Value(100 * i)),
                When(name__istartswith=term, then=Value(50 * i)),
                When(name__icontains=term, then=Value(30 * i)),
                When(tags__icontains=term, then=Value(20 * i)),
                When(services__name__icontains=term, then=Value(15 * i)),
                When(short_description__icontains=term, then=Value(10 * i)),
                When(categories__name__icontains=term, then=Value(8 * i)),
                When(description__icontains=term, then=Value(5 * i)),
            ])
        companies_queryset = companies_queryset.annotate(
            relevance=Case(*relevance_conditions, default=Value(0), output_field=IntegerField())
        )
        # Применяем сначала наш приоритет, а потом уже релевантность
        companies_queryset = companies_queryset.order_by(*primary_sort_order, '-relevance', '-created_at')
    
    else:  # Если нет поиска или выбрана другая сортировка
        sort_field = '-created_at'  # Сортировка по умолчанию
        if sort_by == 'name':
            sort_field = 'name'
        elif sort_by == 'newest':
            sort_field = '-created_at'
        elif sort_by == 'oldest':
            sort_field = 'created_at'
        elif sort_by == 'rating':
            # Добавляем сортировку по рейтингу
            sort_field = '-average_rating'
        
        # Применяем сначала наш приоритет, а потом выбранную пользователем сортировку
        companies_queryset = companies_queryset.order_by(*primary_sort_order, sort_field)

    # --- ОСТАЛЬНОЙ КОД ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ ---

    # Обработка тегов
    for company in companies_queryset:
        if company.tags:
            company.tag_list = [tag.strip() for tag in company.tags.split(',')]
        else:
            company.tag_list = []

    # Пагинация
    paginator = Paginator(companies_queryset, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Категории и города для фильтров
    all_categories = Category.objects.annotate(company_count=Count('company')).order_by('name')
    available_cities = Company.objects.exclude(service_area__exact='').values_list('service_area', flat=True).distinct().order_by('service_area')

    total_results = companies_queryset.count()

    context = {
        'page_obj': page_obj,
        'company_list': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_results': total_results,
        'all_categories': all_categories,
        'available_cities': available_cities,
        'selected_category_ids': selected_category_ids,
        'selected_cities': selected_cities,
        'min_rating': min_rating_str,
    }
    
    return render(request, 'directory/company_list.html', context)
# Файл: directory/views.py




# Файл: directory/views.py

# ... (все ваши импорты вверху файла) ...

def company_detail_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # --- НОВАЯ ЛОГИКА: Сохранение истории просмотров в сессию ---
    viewed_companies = request.session.get('viewed_companies', [])

    # Убираем ID, если он уже был, чтобы переместить его в начало
    if company_id in viewed_companies:
        viewed_companies.remove(company_id)

    # Добавляем ID текущей компании в начало списка
    viewed_companies.insert(0, company_id)

    # Ограничиваем историю последними 10 компаниями
    request.session['viewed_companies'] = viewed_companies[:10]
    # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

    all_reviews = company.reviews.all()
    average_rating = all_reviews.aggregate(Avg('rating')).get('rating__avg')

    # Логика сортировки отзывов с закреплением
    sorted_reviews = []
    user_review = None
    if request.user.is_authenticated:
        other_reviews = []
        for review in all_reviews:
            if review.user == request.user: user_review = review
            else: other_reviews.append(review)
        if user_review: sorted_reviews.append(user_review)
        sorted_reviews.extend(other_reviews)
    else:
        sorted_reviews = all_reviews
# --- НОВАЯ ЛОГИКА: ПРОВЕРКА ВОЗМОЖНОСТИ ОСТАВИТЬ ОТЗЫВ ---
    can_leave_review = False
    has_made_application = False
    has_already_reviewed = False # Флаг: оставлял ли пользователь УЖЕ отзыв

    if request.user.is_authenticated:
        # 1. Проверяем, оставлял ли текущий пользователь заявку для этой компании
        has_made_application = Application.objects.filter(user=request.user, company=company).exists()
        
        # 2. Проверяем, оставлял ли текущий пользователь уже отзыв для этой компании
        has_already_reviewed = Review.objects.filter(user=request.user, company=company).exists()
        
        # 3. Разрешаем оставить отзыв, если есть заявка И еще нет отзыва
        can_leave_review = has_made_application and not has_already_reviewed
    # --- КОНЕЦ НОВОЙ ЛОГИКИ ПРОВЕРКИ ---
    # Инициализируем формы
    request_form = RequestForm()
    review_form = ReviewForm()

    # Обработка POST-запросов (этот блок без изменений)
    if request.method == 'POST':
        if 'submit_request' in request.POST:
            if not request.user.is_authenticated: return redirect('login')
            
            request_form = RequestForm(request.POST, request.FILES, company=company)
            
            if request_form.is_valid():
                user = request.user
                
                # Сохраняем все данные из формы в объект заявки
                new_application = Application.objects.create(
                    user=user, 
                    company=company, 
                    message=request_form.cleaned_data['message'], 
                    attachment=request_form.cleaned_data.get('attachment'),
                    selected_service=request_form.cleaned_data.get('selected_service'),
                    desired_date=request_form.cleaned_data.get('desired_date'),
                )
                
                # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Обновляем тело письма ---
                
                # Получаем полное имя пользователя (Имя + Фамилия)
                user_full_name = user.get_full_name()
                
                service_name = new_application.selected_service.name if new_application.selected_service else "Не указана"
                date_str = new_application.desired_date.strftime("%d.%m.%Y") if new_application.desired_date else "Не указана"
                
                subject = f"Новая заявка с сайта Serviko для '{company.name}'"
                email_body = f"""
                Вы получили новую заявку!

                ДАННЫЕ КЛИЕНТА:
                --------------------------
                Имя: {user_full_name}
                Логин: {user.username}
                Email для связи: {user.email}

                ДЕТАЛИ ЗАЯВКИ:
                --------------------------
                Выбранная услуга: {service_name}
                Желаемая дата: {date_str}
                
                Сообщение:
                {new_application.message}
                --------------------------

                Пожалуйста, свяжитесь с клиентом для уточнения деталей.
                """
                
                email = EmailMessage(subject, email_body, settings.DEFAULT_FROM_EMAIL, [company.email])
                if new_application.attachment:
                    email.attach_file(new_application.attachment.path)
                email.send()
                
                messages.success(request, 'Ваша заявка была успешно отправлена!')
                return redirect('company-detail', company_id=company.id)


        elif 'submit_review' in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, 'Для написания отзыва необходимо войти в аккаунт.')
                return redirect('login')
            
            # --- ГЛАВНАЯ ПРОВЕРКА ДЛЯ ОТЗЫВА ПЕРЕД СОХРАНЕНИЕМ ---
            if not has_made_application: # Проверка на наличие заявки
                messages.error(request, 'Вы можете оставить отзыв только для компаний, которым отправляли заявку.')
                # Здесь важно повторно инициализировать request_form, чтобы она была доступна
                request_form = RequestForm(company=company) 
                return render(request, 'directory/company_detail.html', {
                    'company': company,
                    'reviews': sorted_reviews,
                    'average_rating': average_rating,
                    'total_reviews': all_reviews.count(),
                    'request_form': request_form,
                    'review_form': review_form, # Передаем review_form, чтобы она была пустой, но без ошибок
                    'can_leave_review': can_leave_review, 
                    'has_already_reviewed': has_already_reviewed, 
                    'has_made_application': has_made_application,
                })
            
            if has_already_reviewed: # Проверка, оставлял ли уже отзыв
                messages.error(request, 'Вы уже оставили отзыв для этой компании.')
                # Повторно инициализируем формы, чтобы они были доступны
                request_form = RequestForm(company=company) 
                review_form = ReviewForm() 
                return render(request, 'directory/company_detail.html', {
                    'company': company,
                    'reviews': sorted_reviews,
                    'average_rating': average_rating,
                    'total_reviews': all_reviews.count(),
                    'request_form': request_form,
                    'review_form': review_form,
                    'can_leave_review': can_leave_review, 
                    'has_already_reviewed': has_already_reviewed, 
                    'has_made_application': has_made_application,
                })

            review_form = ReviewForm(request.POST) # Инициализация формы отзыва для POST-запроса
            if review_form.is_valid():
                new_review = review_form.save(commit=False)
                new_review.company = company
                new_review.user = request.user
                new_review.save()
                messages.success(request, 'Ваш отзыв успешно добавлен!')
                return redirect('company-detail', company_id=company.id)
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме отзыва.')
                # Если форма отзыва невалидна, инициализируем request_form для GET-контекста
                request_form = RequestForm(company=company) # Инициализация для GET-контекста
                # Дальнейшая часть кода будет выполняться для отображения страницы с ошибками формы отзыва

    # --- ПОДГОТОВКА ДАННЫХ ДЛЯ GET-ЗАПРОСА ---
    
    # --- ИСПРАВЛЕНИЕ 2: Используем правильное имя переменной ---
    request_form = RequestForm(company=company)
    review_form = ReviewForm()
            
            
    if company.tags:
        company.tag_list = [tag.strip() for tag in company.tags.split(',')]
    else:
        company.tag_list = []
        
    context = {
        'company': company,
        'reviews': sorted_reviews,
        'average_rating': average_rating,
        'total_reviews': all_reviews.count(),
        'request_form': request_form,
        'review_form': review_form,
        'can_leave_review': can_leave_review,        # <-- Добавить
        'has_already_reviewed': has_already_reviewed, # <-- Добавить
        'has_made_application': has_made_application, # <-- Добавить
    }
    return render(request, 'directory/company_detail.html', context)



def search_autocomplete(request):
    """API для автодополнения поиска (работает с кириллицей!)"""
    from django.db.models.functions import Lower
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    query_lower = query.lower()
    
    # Поиск по названиям компаний - используем Lower() для кириллицы
    companies = Company.objects.annotate(
        name_lower=Lower('name')
    ).filter(
        name_lower__contains=query_lower
    ).values_list('name', flat=True)[:5]
    
    for company in companies:
        suggestions.append({
            'text': company,
            'type': 'company',
            'icon': '🏢'
        })
    
    # Поиск по тегам
    tags_queryset = Company.objects.annotate(
        tags_lower=Lower('tags')
    ).filter(
        tags_lower__contains=query_lower
    ).exclude(tags='').values_list('tags', flat=True)
    
    unique_tags = set()
    for tags_string in tags_queryset:
        if tags_string:
            for tag in tags_string.split(','):
                tag = tag.strip()
                if query_lower in tag.lower() and len(unique_tags) < 3:
                    unique_tags.add(tag)
    
    for tag in unique_tags:
        suggestions.append({
            'text': tag,
            'type': 'tag',
            'icon': '🏷️'
        })
    
    # Поиск по категориям
    categories = Category.objects.annotate(
        name_lower=Lower('name')
    ).filter(
        name_lower__contains=query_lower
    ).values_list('name', flat=True)[:3]
    
    for category in categories:
        suggestions.append({
            'text': category,
            'type': 'category',
            'icon': '📁'
        })
    
    return JsonResponse({'suggestions': suggestions[:10]})
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя, но не активируем его
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # --- Логика отправки письма для активации ---
            current_site = get_current_site(request)
            mail_subject = 'Активируйте ваш аккаунт на Serviko'
            
            message = render_to_string('directory/activation_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            # Отправляем email (в консоль)
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            
            # Показываем пользователю страницу с сообщением "Проверьте почту"
            return render(request, 'directory/activation_sent.html')
    else:
        form = CustomUserCreationForm()
        
    context = {'form': form}
    return render(request, 'directory/register.html', context)

def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Ваш аккаунт успешно активирован! Теперь вы можете войти.')
        return redirect('login')
    else:
        messages.error(request, 'Ссылка для активации недействительна!')
        return redirect('company-list')
@login_required
def toggle_favorite_view(request, company_id):
    # Проверяем, что запрос сделан через POST для безопасности
    if request.method == 'POST':
        company = get_object_or_404(Company, id=company_id)
        user = request.user
        
        # Если компания уже в избранном - удаляем. Иначе - добавляем.
        if company in user.favorite_companies.all():
            user.favorite_companies.remove(company)
            is_favorited = False
        else:
            user.favorite_companies.add(company)
            is_favorited = True
            
        return JsonResponse({'status': 'ok', 'is_favorited': is_favorited})
    
    # Если не POST-запрос, возвращаем ошибку
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Проверка: убеждаемся, что текущий пользователь является автором отзыва
    if review.user != request.user:
        return HttpResponseForbidden("У вас нет прав для удаления этого отзыва.")

    # Мы удаляем только через POST-запрос для безопасности
    if request.method == 'POST':
        company_id = review.company.id
        review.delete()
        messages.success(request, 'Ваш отзыв был успешно удален.')
        # Перенаправляем обратно на страницу компании
        return redirect('company-detail', company_id=company_id)
    
    # Если это был не POST-запрос, просто возвращаем на страницу компании
    return redirect('company-detail', company_id=review.company.id)


@login_required
def profile_view(request):
    # Определяем, какая вкладка должна быть активной, по умолчанию - 'edit'
    active_tab = request.GET.get('tab', 'edit')

    # --- Обработка форм редактирования профиля (если данные были отправлены) ---
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            return redirect('profile') # Перенаправляем на ту же страницу
    else:
        # Если страница просто открыта, показываем формы с текущими данными
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)

    # --- Собираем данные для всех остальных вкладок ---
    favorite_companies = request.user.favorite_companies.all()
    user_applications = Application.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)
    
    viewed_company_ids = request.session.get('viewed_companies', [])
    companies_dict = {c.id: c for c in Company.objects.filter(id__in=viewed_company_ids)}
    viewed_companies_list = [companies_dict[id] for id in viewed_company_ids if id in companies_dict]
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'favorite_list': favorite_companies,
        'application_list': user_applications,
        'review_list': user_reviews,
        'history_list': viewed_companies_list,
        'active_tab': active_tab, # Передаем имя активной вкладки в шаблон
    }
    return render(request, 'directory/profile.html', context)



@login_required
def admin_dashboard_data(request):
    """
    API для расширенной, ролевой аналитической панели с фильтрацией по компании и датам.
    """
    start_date, end_date = None, None
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')
    
    if start_date_str and end_date_str and start_date_str != '' and end_date_str != '':
        start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%d')
        start_date = make_aware(start_date_naive)
        end_date = make_aware(end_date_naive + timedelta(days=1))
    
    if not start_date or not end_date:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

    target_company_id = request.GET.get('company_id')
    
    if request.user.is_superuser:
        all_companies = Company.objects.all()
        if target_company_id:
            companies_qs = all_companies.filter(id=target_company_id)
        else:
            companies_qs = all_companies
    else:
        all_companies = Company.objects.filter(owner=request.user)
        if target_company_id and all_companies.filter(id=target_company_id).exists():
            companies_qs = all_companies.filter(id=target_company_id)
        else:
            companies_qs = all_companies

    kpi_data = {
        'total_applications': Application.objects.filter(company__in=companies_qs).count(),
        'total_reviews': Review.objects.filter(company__in=companies_qs).count(),
        'average_rating': Review.objects.filter(company__in=companies_qs).aggregate(avg=Avg('rating'))['avg'] or 0,
    }
    if request.user.is_superuser and not target_company_id:
        kpi_data['total_users'] = User.objects.count()
        kpi_data['total_companies'] = all_companies.count()

    labels = []
    current_date = start_date
    while current_date.date() < end_date.date():
        labels.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    applications_qs = Application.objects.filter(created_at__range=(start_date, end_date), company__in=companies_qs)
    reviews_qs = Review.objects.filter(created_at__range=(start_date, end_date), company__in=companies_qs)
    
    applications_data = { d['date'].strftime('%Y-%m-%d'): d['count'] for d in applications_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')) }
    reviews_data = { d['date'].strftime('%Y-%m-%d'): d['count'] for d in reviews_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')) }
    
    top_companies_by_apps = []
    rating_distribution = []
    most_active_users = []

    if request.user.is_superuser and not target_company_id:
        top_companies_qs = Company.objects.annotate(count=Count('application')).filter(count__gt=0).order_by('-count')[:5]
        top_companies_by_apps = list(top_companies_qs.values('name', 'count'))
        
        rating_dist_qs = Review.objects.values('rating').annotate(count=Count('id')).order_by('rating')
        rating_distribution = list(rating_dist_qs)

        active_users_qs = User.objects.annotate(count=Count('review')).filter(count__gt=0).order_by('-count')[:5]
        most_active_users = list(active_users_qs.values('username', 'count'))

    data = {
        'kpi': kpi_data,
        'charts': {
            'labels': labels,
            'applications': [applications_data.get(date, 0) for date in labels],
            'reviews': [reviews_data.get(date, 0) for date in labels],
        },
        'filters': {
            'companies_for_select': list(all_companies.values('id', 'name')),
        },
        'extra_metrics': {
            'top_companies_by_apps': top_companies_by_apps,
            'rating_distribution': rating_distribution,
            'most_active_users': most_active_users,
        }
    }
    if request.user.is_superuser and not target_company_id:
        registrations_qs = User.objects.filter(date_joined__range=(start_date, end_date))
        registrations_data = {d['date'].strftime('%Y-%m-%d'): d['count'] for d in registrations_qs.annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id'))}
        data['charts']['registrations'] = [registrations_data.get(date, 0) for date in labels]

    return JsonResponse(data)


    # Файл: directory/views.py

def homepage_view(request):
    """
    Отображает новую главную страницу (overview) с дополнительными блоками.
    """
    # Находим 6 самых популярных категорий (по количеству компаний в них)
    popular_categories = Category.objects.annotate(
        num_companies=Count('company')
    ).order_by('-num_companies')[:6]

    # Находим 4 компании, отмеченные как "популярные" в админке
    popular_companies = Company.objects.filter(is_popular=True)[:4]

    # --- НОВЫЙ КОД: Находим 3 свежих отзыва с оценкой 5 ---
    latest_reviews = Review.objects.filter(rating=5).order_by('-created_at')[:3]

    context = {
        'popular_categories': popular_categories,
        'popular_companies': popular_companies,
        'latest_reviews': latest_reviews, # <-- Передаем отзывы в шаблон
    }
    return render(request, 'directory/homepage.html', context)


def partnership_request_view(request):
    if request.method == 'POST':
        form = PartnershipRequestForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            subject = f"Новая заявка на партнерство: {data['company_name']}"
            email_body = f"""
            Новая заявка на добавление компании на сайт Serviko!

            Название компании: {data['company_name']}
            Контактное лицо: {data['contact_person']}
            Email: {data['email']}
            Телефон: {data['phone_number']}

            Комментарий:
            {data.get('comment', 'Не указан')}
            """

            email = EmailMessage(
                subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL], # Отправляем на email админа
            )

            # Прикрепляем файл, если он есть
            if 'attachment' in request.FILES:
                file = request.FILES['attachment']
                email.attach(file.name, file.read(), file.content_type)

            email.send()

            messages.success(request, 'Ваша заявка на партнерство успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect('homepage')
    else:
        form = PartnershipRequestForm()

    return render(request, 'directory/partnership_request.html', {'form': form})


def legal_info_view(request):
    """Отображает страницу с юридической информацией (условия, политика конфиденциальности)."""
    return render(request, 'directory/legal_info.html')