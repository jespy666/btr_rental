import os
from dotenv import load_dotenv

from django.db import models
from django.utils.translation import gettext as _
from django.db.models.signals import post_save, pre_save
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


@receiver(post_save, sender=Booking)
def booking_created_receiver(sender, instance, created, **kwargs):
    from btr.bookings.tasks import send_booking_notify
    if created:
        load_dotenv()
        access_token = os.getenv('VK_BTR_KEY')
        user_id = os.getenv('VK_ADMIN_ID')
        message = _(
            '#{id}\n'
            'User with name {name} book a ride just now!\n'
            'User phone: {phone}\n'
            'Date: {date}\nTime: {start}-{end}\n'
            'Bikes requested: {bike}\n'
            'Awaiting confirmation...'
        ).format(
            id=instance.pk,
            name=instance.rider.first_name,
            phone=instance.rider.phone_number,
            date=instance.booking_date,
            start=instance.start_time,
            end=instance.end_time,
            bike=instance.bike_count,
        )
        send_booking_notify.delay(user_id, access_token, message)


@receiver(pre_save, sender=Booking)
def booking_created_receiver(sender, instance, **kwargs):
    from btr.bookings.tasks import send_booking_notify
    try:
        old_status = Booking.objects.get(pk=instance.pk).status
    except Booking.DoesNotExist:
        return
    user_id = os.getenv('VK_ADMIN_ID')
    access_token = os.getenv('VK_BTR_KEY')
    if old_status == 'pending' and instance.status == 'confirmed':
        message = _(
            'Booking #{id} confirmed by admin'
        ).format(id=instance.pk)
        send_booking_notify.delay(user_id, access_token, message)
