import os
from dotenv import load_dotenv

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from .models import Booking
from ..tasks.book_tasks import send_booking_notify


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
def create_booking_notify(sender, instance, created, **kwargs):
    if created:
        load_dotenv()
        access_token = os.getenv('VK_BTR_KEY')
        user_id = os.getenv('VK_ADMIN_ID')
        if instance.rider.username == 'admin':
            message = _(
                '#{id}\n'
                'Admin make foreign book just now!\n'
                'Client phone: {phone}\n'
                'Date: {date}\nTime: {start}-{end}\n'
                'Bikes booked: {bike}\n'
            ).format(
                id=instance.pk,
                phone=instance.foreign_number,
                date=instance.booking_date,
                start=instance.start_time,
                end=instance.end_time,
                bike=instance.bike_count,
            )
        else:
            message = _(
                '#{id}\n'
                'User with name {name} book a ride just now!\n'
                'User phone: {phone}\n'
                'Date: {date}\nTime: {start}-{end}\n'
                'Bikes requested: {bike}\n\n'
                'https://t.me/BTRBookingBot'
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


@receiver(post_save, sender=Booking)
def booking_confirm_notify(sender, instance, created, **kwargs):
    if not created:
        user_id = os.getenv('VK_ADMIN_ID')
        access_token = os.getenv('VK_BTR_KEY')
        status = instance.status
        msg = ''
        if status == 'confirmed':
            msg = _(
                'Booking #{id} confirmed by admin'
            ).format(id=instance.pk)
        elif status == 'canceled':
            msg = _(
                'Booking #{id} canceled by admin'
            ).format(id=instance.pk)
        send_booking_notify.delay(user_id, access_token, msg)
