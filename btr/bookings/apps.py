from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BookingsConfig(AppConfig):
    """
    Django app configuration for managing bookings.

    Attributes:
        default_auto_field (str): default auto field for model primary keys.
        name (str): The name of the app.
        verbose_name (str): A human-readable name for the app.

    Example:
        In your Django project, configure the 'Bookings' app using this class.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'btr.bookings'
    verbose_name = _('Bookings')

    def ready(self) -> None:
        # import booking signals
        import btr.bookings.signals  # noqa: F401
