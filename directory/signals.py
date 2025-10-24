# Файл: directory/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Создает профиль пользователя при создании нового User 
    или просто убеждается, что он существует при обновлении User.
    """
    if created:
        # Если пользователь НОВЫЙ, создаем для него профиль.
        UserProfile.objects.create(user=instance)
    
    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Для СУЩЕСТВУЮЩЕГО пользователя, мы просто убеждаемся, что профиль есть.
    # Метод get_or_create идеально подходит: он либо найдет, либо создаст.
    UserProfile.objects.get_or_create(user=instance)