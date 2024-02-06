from django.db import models
from django.utils.translation import gettext_lazy as _

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

    bike_count = models.CharField(
        max_length=2,
        blank=False,
        verbose_name=_('bikes in rent')
    )

    STATUS_CHOICES = [
        (_('pending'), _('wait to confirm')),
        (_('confirmed'), _('accepted')),
        (_('completed'), _('finished')),
        (_('canceled'), _('canceled')),
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

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
