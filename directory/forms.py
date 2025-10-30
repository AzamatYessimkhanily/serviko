# Файл: directory/forms.py
from django import forms
from .models import Company, Category, Application, Review, UserProfile, Service # <-- Обновлено: все нужные модели
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # <-- ВАЖНО: Добавлен импорт для локализации


class RequestForm(forms.Form):
    selected_service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        label=_("Конкретная услуга (необязательно)"), # <-- Локализовано
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    desired_date = forms.DateField(
        required=False,
        label=_("Желаемая дата выполнения"), # <-- Локализовано
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': _('Опишите вашу задачу...')}), # <-- Локализовано
        label=_("Сообщение") # <-- Локализовано
    )
    attachment = forms.FileField(
        required=False, 
        label=_("Прикрепить файл"), # <-- Локализовано
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['selected_service'].queryset = company.services.all()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Оставьте свой комментарий...')}), # <-- Локализовано
            'rating': forms.Select(attrs={'class': 'rating-select'}),
        }
        labels = {
            'rating': _('Ваша оценка'), # <-- Локализовано
            'comment': _('Комментарий'), # <-- Локализовано
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text=_('Обязательное поле. На этот email будут приходить уведомления.'), # <-- Локализовано
        label=_('Email') # <-- Добавлено
    )
    first_name = forms.CharField(max_length=30, required=True, label=_('Имя')) # <-- Локализовано
    last_name = forms.CharField(max_length=150, required=True, label=_('Фамилия')) # <-- Локализовано

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        labels = { # <-- Добавлены метки для стандартных полей User
            'username': _('Логин'),
            'password': _('Пароль'),
            'password2': _('Подтверждение пароля'),
        }


class UserUpdateForm(forms.ModelForm):
    """Форма для редактирования основной информации пользователя."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': _('Логин'), # <-- Локализовано
            'first_name': _('Имя'), # <-- Локализовано
            'last_name': _('Фамилия'), # <-- Локализовано
            'email': _('Email'), # <-- Локализовано
        }


class ProfileUpdateForm(forms.ModelForm):
    """Форма для редактирования аватара."""
    class Meta:
        model = UserProfile
        fields = ['avatar']
        labels = {'avatar': _('Новый аватар')} # <-- Локализовано


class PartnershipRequestForm(forms.Form):
    company_name = forms.CharField(label=_("Название компании/ТОО"), max_length=200) # <-- Локализовано
    contact_person = forms.CharField(label=_("Контактное лицо (ФИО)"), max_length=200) # <-- Локализовано
    email = forms.EmailField(label=_("Ваш Email")) # <-- Локализовано
    phone_number = forms.CharField(label=_("Номер телефона"), max_length=20) # <-- Локализовано
    site = forms.CharField(label=_("Сайт"), max_length=200, required=False) # <-- Локализовано
    comment = forms.CharField(
        label=_("Дополнительно о себе"), # <-- Локализовано
        widget=forms.Textarea(attrs={'rows': 4}), 
        required=False
    )