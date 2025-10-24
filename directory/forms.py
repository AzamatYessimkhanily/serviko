# Файл: directory/forms.py
from .models import Service # <-- Добавьте этот импорт
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# Файл: directory/forms.py

# Файл: directory/forms.py

class RequestForm(forms.Form):
    selected_service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        label="Конкретная услуга (необязательно)",
        widget=forms.Select(attrs={'class': 'form-select'}) # <-- Добавлен класс
    )
    desired_date = forms.DateField(
        required=False,
        label="Желаемая дата выполнения",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) # <-- Добавлен класс
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Опишите вашу задачу...'}), # <-- Добавлен класс
        label="Сообщение"
    )
    attachment = forms.FileField(
        required=False, 
        label="Прикрепить файл",
        widget=forms.FileInput(attrs={'class': 'form-control'}) # <-- Добавлен класс
    )

    def __init__(self, *args, **kwargs):
        # Эта логика получает компанию из view
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # И на основе компании фильтрует список услуг
        if company:
            self.fields['selected_service'].queryset = company.services.all()

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Оставьте свой комментарий...'}),
            'rating': forms.Select(attrs={'class': 'rating-select'}), # Можно добавить класс для стилизации звезд
        }
        labels = {
            'rating': 'Ваша оценка',
            'comment': 'Комментарий',
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Обязательное поле. На этот email будут приходить уведомления.')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=150, required=True, label='Фамилия')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

class UserUpdateForm(forms.ModelForm):
    """Форма для редактирования основной информации пользователя."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {'username': 'Логин', 'first_name': 'Имя', 'last_name': 'Фамилия'}

class ProfileUpdateForm(forms.ModelForm):
    """Форма для редактирования аватара."""
    class Meta:
        model = UserProfile
        fields = ['avatar']
        labels = {'avatar': 'Новый аватар'}

class PartnershipRequestForm(forms.Form):
    company_name = forms.CharField(label="Название компании/ТОО", max_length=200)
    contact_person = forms.CharField(label="Контактное лицо (ФИО)", max_length=200)
    email = forms.EmailField(label="Ваш Email")
    phone_number = forms.CharField(label="Номер телефона", max_length=20)
    site = forms.CharField(label="Сайт", max_length=200, required=False)
    comment = forms.CharField(label="Дополнительно о себе", widget=forms.Textarea(attrs={'rows': 4}), required=False)


