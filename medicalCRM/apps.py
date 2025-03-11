from django.apps import AppConfig


class MedicalcrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medicalCRM'

    def ready(self):
        import medicalCRM.signals  # ✅ Добавь эту строку, если её нет