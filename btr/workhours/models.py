from django.db import models
from django.utils.translation import gettext_lazy as _


class WorkHours(models.Model):

    objects = None
    DAY_CHOICES = [
        ('Workday', _('Working day')),
        ('Weekend', _('Weekend day')),
    ]

    day = models.CharField(
        max_length=7,
        choices=DAY_CHOICES,
        verbose_name=_('Weekday')
    )
    open = models.TimeField(blank=False, verbose_name=_('Open hours'))
    close = models.TimeField(blank=False, verbose_name=_('Close hours'))

    def __str__(self):
        return f'{self.open}-{self.close}'

    class Meta:
        verbose_name = _('Work hour')
        verbose_name_plural = _('Work hours')
