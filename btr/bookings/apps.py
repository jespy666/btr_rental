from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'btr.bookings'

    def ready(self):
        import btr.bookings.signals  # noqa: F401
