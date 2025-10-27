from django.apps import AppConfig

class MscarAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mscar_app'
    
    def ready(self):
        import mscar_app.signals