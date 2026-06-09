from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuração do app da API REST."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
