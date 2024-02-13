from celery import shared_task
from django.utils import timezone

from btr.bookings.models import Booking
from ..emails import (create_booking_mail, confirm_booking_mail,
                      cancel_booking_mail)
from ..celery import app


@app.task
def send_booking_details(email: str, name: str, date: str, status: str,
                         start: str, end: str, bikes: str, pk: str) -> None:
    """Send mail to user after booking create"""
    create_booking_mail(email, name, date, status, start, end, bikes, pk)


@app.task
def send_confirm_message(email: str, pk: str, bikes: str, date: str,
                         start: str, end: str) -> None:
    """Send mail to user when booking confirmed"""
    confirm_booking_mail(email, pk, bikes, date, start, end)


@app.task
def send_cancel_message(email: str, pk: str, bikes: str, date: str,
                        start: str, end: str) -> None:
    """Send mail to user when booking canceled by admin"""
    cancel_booking_mail(email, pk, bikes, date, start, end)


@app.task
def send_cancel_self_message(email: str, pk: str, bikes: str, date: str,
                             start: str, end: str) -> None:
    """Send mail to user when booking canceled by himself"""
    cancel_booking_mail(email, pk, bikes, date, start, end, self_cancel=True)


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
