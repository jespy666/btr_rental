from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """
    Configuration for the Users app.

    Attributes:
        default_auto_field (str): The name of the default auto-generated
         primary key field.
        name (str): The name of the app.
        verbose_name (str): A human-readable name for the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'btr.users'
    verbose_name = _('Users')

    def ready(self):
        # import SiteUser signals
        import btr.users.signals  # noqa: F401
