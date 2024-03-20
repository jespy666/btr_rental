from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkHoursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'btr.workhours'
    verbose_name = _('Working hours')

    def ready(self):
        import btr.workhours.signals  # noqa: F401
