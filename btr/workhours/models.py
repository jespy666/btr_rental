from django.db import models
from django.utils.translation import gettext_lazy as _


class WorkHours(models.Model):

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


class DayControl(models.Model):

    date = models.DateField(
        verbose_name=_('Date'),
        blank=False,
    )
    open = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_('Open hours')
    )
    close = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_('Close hours')
    )
    is_closed = models.BooleanField(
        verbose_name=_('All day closed'),
        default=False,
    )

    def __str__(self):
        return f'{self.date}: {self.open} - {self.close}'

    class Meta:
        verbose_name = _('Day')
        verbose_name_plural = _('Days settings')
