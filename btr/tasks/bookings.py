from celery import shared_task
from django.utils import timezone

from btr.bookings.models import Booking
from ..emails import (create_booking_mail, confirm_booking_mail,
                      cancel_booking_mail, edit_booking_mail)
from ..celery import app


@app.task
def send_booking_details(**kwargs) -> None:
    """Send mail to user after booking create"""
    create_booking_mail(
        kwargs.get('email'),
        kwargs.get('name'),
        kwargs.get('date'),
        kwargs.get('status'),
        kwargs.get('start'),
        kwargs.get('end'),
        kwargs.get('bikes'),
        kwargs.get('pk'),
    )


@app.task
def send_confirm_message(**kwargs) -> None:
    """Send mail to user when booking confirmed"""
    confirm_booking_mail(
        kwargs.get('email'),
        kwargs.get('pk'),
        kwargs.get('bikes'),
        kwargs.get('date'),
        kwargs.get('start'),
        kwargs.get('end'),
    )


@app.task
def send_cancel_message(**kwargs) -> None:
    """Send mail to user when booking canceled by admin"""
    cancel_booking_mail(
        kwargs.get('email'),
        kwargs.get('pk'),
        kwargs.get('bikes'),
        kwargs.get('date'),
        kwargs.get('start'),
        kwargs.get('end'),
    )


@app.task
def send_cancel_self_message(**kwargs) -> None:
    """Send mail to user when booking canceled by himself"""
    cancel_booking_mail(
        kwargs.get('email'),
        kwargs.get('pk'),
        kwargs.get('bikes'),
        kwargs.get('date'),
        kwargs.get('start'),
        kwargs.get('end'),
        self_cancel=True,
    )


@app.task
def send_edit_booking_message(**kwargs) -> None:
    edit_booking_mail(
        kwargs.get('email'),
        kwargs.get('pk'),
        kwargs.get('bikes'),
        kwargs.get('date'),
        kwargs.get('start'),
        kwargs.get('end'),
    )


@app.task
def send_self_edit_booking_message(**kwargs) -> None:
    edit_booking_mail(
        kwargs.get('email'),
        kwargs.get('pk'),
        kwargs.get('bikes'),
        kwargs.get('date'),
        kwargs.get('start'),
        kwargs.get('end'),
        self_edit=True,
    )


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
