from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    label = 'user_account'  # Унікальний label для уникнення конфлікту з allauth.account
