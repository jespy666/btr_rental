from datetime import datetime

from django.utils.translation import gettext as _

from celery import shared_task

from btr.bookings.models import Booking
from ..emails import (create_booking_mail, confirm_booking_mail,
                      cancel_booking_mail, edit_booking_mail)
from ..celery import app


@app.task
def send_booking_details(**kwargs) -> None:
    """
    Email the user after booking creation.

    Args:
        **kwargs: Keyword arguments containing booking details.

    Example:
        send_booking_details(
            email='user@example.com',
            name='John Doe',
            date='2024-03-29',
            status='confirmed',
            start='10:00',
            end='11:00',
            bikes='2',
            pk='123'
        )
    """
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
    """
    Email the user after booking is confirmed by admin.

    Args:
        **kwargs: Keyword arguments containing booking details.

    Example:
        send_booking_details(
            email='user@example.com',
            date='2024-03-29',
            start='10:00',
            end='11:00',
            bikes='2',
            pk='123'
        )
    """
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
    """
    Email the user after booking canceled by admin.

    Args:
        **kwargs: Keyword arguments containing booking details.

    Example:
        send_booking_details(
            email='user@example.com',
            date='2024-03-29',
            start='10:00',
            end='11:00',
            bikes='2',
            pk='123'
        )
    """
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
    """
    Email the user after booking canceled by himself.

    Args:
        **kwargs: Keyword arguments containing booking details.

    Example:
        send_booking_details(
            email='user@example.com',
            date='2024-03-29',
            start='10:00',
            end='11:00',
            bikes='2',
            pk='123'
        )
    """
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
    """
    Email the user after booking edited by admin.

    Args:
        **kwargs: Keyword arguments containing booking details.

    Example:
        send_booking_details(
            email='user@example.com',
            date='2024-03-29',
            start='10:00',
            end='11:00',
            bikes='2',
            pk='123'
        )
    """
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
    """
    Email the user after booking edited by himself.

    Args:
        **kwargs: Keyword arguments containing booking details.

    Example:
        send_booking_details(
            email='user@example.com',
            date='2024-03-29',
            start='10:00',
            end='11:00',
            bikes='2',
            pk='123'
        )
    """
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
def check_booking_status() -> None:
    """
    Automatically set booking status to 'completed' after the booking end time.

    Example:
        This task runs periodically and updates the status of confirmed
         bookings whose end time has passed.
    """
    current_time = datetime.utcnow()
    current_date = datetime.utcnow().date()
    bookings_to_complete = Booking.objects.filter(
        status=_('confirmed'),
        booking_date__lte=current_date,
        end_time__gte=current_time,
    )
    for booking in bookings_to_complete:
        booking.status = _('completed')
        booking.save()
