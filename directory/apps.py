from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'directory'
    def ready(self):
        import directory.signals # <-- Эта строка должна здесь быть