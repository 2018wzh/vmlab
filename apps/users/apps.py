from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = '用户管理'

    def ready(self):
        from .signals import create_initial_roles_and_users
        post_migrate.connect(create_initial_roles_and_users, sender=self)
