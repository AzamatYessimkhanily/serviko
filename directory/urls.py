# directory/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Основные страницы
    path('', views.homepage_view, name='homepage'),
    path('catalog/', views.company_list_view, name='company-list'),
    path('company/<int:company_id>/', views.company_detail_view, name='company-detail'),
    
    # Регистрация
    path('register/', views.register_view, name='register'),
    
    # Вход
    path('login/', auth_views.LoginView.as_view(template_name='directory/login.html'), name='login'),
    
    # ВЫХОД (ИЗМЕНЕННАЯ ЛОГИКА)
    # Теперь после выхода пользователь будет сразу перенаправлен на главную страницу ('company-list')
    path('logout/', auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),

    # API для автодополнения (из вашего кода)
    path('api/search/autocomplete/', views.search_autocomplete, name='search-autocomplete'),
    path('company/<int:company_id>/favorite/', views.toggle_favorite_view, name='toggle-favorite'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete-review'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='directory/password_reset_form.html'), 
         name='password_reset'),
         
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='directory/password_reset_done.html'), 
         name='password_reset_done'),
         
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='directory/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='directory/password_reset_complete.html'), 
         name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    path('api/admin-dashboard-data/', views.admin_dashboard_data, name='admin-dashboard-data'),
    path('partnership/', views.partnership_request_view, name='partnership-request'),
     path('legal-info/', views.legal_info_view, name='legal-info'), # <-- Добавьте эту строку
]