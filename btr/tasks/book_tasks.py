from celery import shared_task
from django.utils import timezone

from btr.bookings.models import Booking

from ..emails import send_booking_details
from ..vk import SendBookingNotification
from ..celery import app


@app.task
def send_details(user_email, date, start, end, bike_count):
    send_booking_details(user_email, date, start, end, bike_count)


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
