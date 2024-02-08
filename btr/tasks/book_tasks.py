from celery import shared_task
from django.utils import timezone

from btr.bookings.models import Booking

from ..emails import create_booking_mail
from ..vk import SendBookingNotification
from ..celery import app


@app.task
def send_booking_details(email: str, name: str, date: str, status: str,
                         start: str, end: str, bikes: str, pk: str) -> None:
    """Send mail to user after booking create"""
    create_booking_mail(email, name, date, status, start, end, bikes, pk)


@shared_task
def check_booking_status():
    current_time = timezone.now().time()
    bookings_to_complete = Booking.objects.filter(
        status='confirmed',
        end_time__gte=current_time,
    )
    for booking in bookings_to_complete:
        booking.status = 'completed'
        booking.save()


@app.task
def send_booking_notify(group_id, access_token, message):
    vk = SendBookingNotification(group_id, access_token)
    vk.send_notify(message)
