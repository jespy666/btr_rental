from django.db import models
from django.utils.translation import gettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver
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


@receiver(post_save, sender=Booking)
def update_user_status(sender, instance, **kwargs):
    """Setting the user level based on the number of rides"""
    rider = instance.rider
    book_count = rider.booking_set.filter(status='completed').count()
    match book_count:
        case count if count < 3:
            rider.status = 'Newbie'
        case count if 3 <= count < 5:
            rider.status = 'Amateur'
        case count if 5 <= count < 10:
            rider.status = 'Professional'
        case _:
            rider.status = 'Master'
    rider.save()
