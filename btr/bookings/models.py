from django.db import models
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField

from btr.users.models import SiteUser


class Booking(models.Model):

    rider = models.ForeignKey(
        SiteUser,
        on_delete=models.PROTECT,
        null=True,
    )

    foreign_number = PhoneNumberField(
        blank=True,
        unique=True,
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
        return (f'Book user {self.rider.id} on {self.booking_date}'
                f' from {self.start_time} to {self.end_time},'
                f' status: {self.status}')
