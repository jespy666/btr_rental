from django.db import models
from django.utils.translation import gettext as _

from phonenumber_field.modelfields import PhoneNumberField

from btr.users.models import SiteUser


class Booking(models.Model):

    rider = models.ForeignKey(
        SiteUser,
        on_delete=models.PROTECT,
    )

    foreign_number = PhoneNumberField(
        blank=True,
        unique=False,
        verbose_name=_('Client\'s phone')
    )

    booking_date = models.DateField(
        blank=False,
        verbose_name=_('Book day'),
    )

    start_time = models.TimeField(
        blank=False,
        verbose_name=_('Time of start'),
    )

    end_time = models.TimeField(
        blank=False,
        verbose_name=_('Time of end')
    )

    bike_count = models.IntegerField(
        blank=False,
        verbose_name=_('bikes_count')
    )

    STATUS_CHOICES = [
        ('pending', _('wait to confirm')),
        ('confirmed', _('accepted')),
        ('completed', _('finished')),
        ('canceled', _('canceled')),
    ]

    status = models.CharField(
        max_length=40,
        verbose_name=_('Status'),
        blank=False,
        choices=STATUS_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        str_view = _(
            'Status: {status}. Date: {date} {start} - {end}'
        ).format(
            status=self.status,
            date=self.booking_date,
            start=self.start_time,
            end=self.end_time,
        )
        return str_view
