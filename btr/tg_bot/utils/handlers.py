import os
import secrets
import string
from typing import List, Tuple

from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiogram.types import ReplyKeyboardMarkup

from django.utils.translation import gettext as _

from .exceptions import TimeIsNotAvailable, CodesCompareError
from btr.tasks.admin import send_vk_notify
from btr.tasks import bookings as book_mail
from btr.tasks import users as user_mail


def check_admin_access(user_id: int) -> bool:
    """
    Check if the current user is an admin.

    Args:
        user_id (int): The user ID to check.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    load_dotenv()
    admin_ids = os.getenv('TG_ADMIN_IDS')
    return user_id in eval(admin_ids)


def extract_start_times(intervals: List[Tuple]) -> List[str]:
    """
    Get all available start times for bot buttons.

    Args:
        intervals (List[Tuple[str, str]]): List of time intervals (start, end).

    Returns:
        List[str]: List of formatted start times.
    """
    start_times = []
    for start, end in intervals:
        start_dt = datetime.strptime(start, '%H:%M')
        end_dt = datetime.strptime(end, '%H:%M')
        hours_difference = (end_dt - start_dt).seconds // 3600
        start_times.extend(
            [(start_dt + timedelta(hours=i)).strftime('%H:%M') for i in
             range(hours_difference)])

    return start_times


def friendly_formatted_date(date: str) -> str:
    """
    Return the date with the month name.

    Args:
        date (str): The input date in the format 'YYYY-MM-DD'.

    Returns:
        str: The formatted date with the month name (e.g., '2024-March-29').
    """
    date_object = datetime.strptime(date, '%Y-%m-%d')
    return date_object.strftime('%Y-%B-%d')


def extract_hours(slots: list, start_time: str) -> list:
    """
    Get a list of available hours for booking.

    Args:
        slots (list): List of time slots (start, end).
        start_time (str): The desired start time in the format 'HH:MM'.

    Returns:
        list: A list of available hours (as strings) from the start time.
    """
    for start, end in slots:
        start_hours = int(start.split(':')[0])
        end_hours = int(end.split(':')[0])
        book_hours = int(start_time.split(':')[0])
        if start_hours <= book_hours < end_hours:
            available_hours = end_hours - book_hours
            return [str(i) for i in range(1, available_hours + 1)]


def get_slots_for_bot_view(slots: list) -> str:
    """
    Show free booking slots for a given date.

    Args:
        slots (list): List of time slots (start, end).

    Returns:
        str: A formatted string with available booking slots.
    """
    bot_view_slots = ''
    for slot in slots:
        bot_view_slots += f'{slot[0]}-{slot[1]}\n'
    return bot_view_slots


def check_available_start_time(start_time: str, slots: list) -> bool:
    """
    Check if the given time is available in the list of free slots.

    Args:
        start_time (str): The desired start time in the format 'HH:MM'.
        slots (list): List of time slots (start, end).

    Returns:
        bool: True if the time is available, False otherwise.

    Raises:
        TimeIsNotAvailable: if start time are already booked or out of time.
    """
    for slot_start, slot_end in slots:
        if slot_start <= start_time < slot_end:
            return True
    raise TimeIsNotAvailable


def get_end_time(start_time: str, hours: str) -> str:
    """
    Calculate the end time based on the given start time and duration in hours.

    Args:
        start_time (str): The start time in the format 'HH:MM'.
        hours (str): The duration in hours.

    Returns:
        str: The calculated end time in the format 'HH:MM'.
    """
    start = datetime.strptime(start_time, "%H:%M")
    end = start + timedelta(hours=int(hours))
    return end.strftime('%H:%M')


def get_hours(start: str, end: str) -> str:
    """
    Calculate the duration between two time points in hours.

    Args:
        start (str): The start time in the format 'HH:MM'.
        end (str): The end time in the format 'HH:MM'.

    Returns:
        str: The duration between start and end time in hours.
    """
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    delta = end_time - start_time
    hours = int(delta.total_seconds() // 3600)
    return str(hours)


def check_available_hours(start_time: str, hours: str, slots: list) -> bool:
    """
    Validate if the given time range is available within the list
     of time slots.

    Args:
        start_time (str): The start time in the format 'HH:MM'.
        hours (str): The duration in hours.
        slots (list): List of time slots represented as tuples (start, end).

    Returns:
        bool: True if the time range is available, False otherwise.

    Raises:
        TimeIsNotAvailable: If the time range is not available within any slot.
    """
    start = datetime.strptime(start_time, '%H:%M')
    end = start + timedelta(hours=int(hours))
    for slot_start, slot_end in slots:
        f_start = datetime.strptime(slot_start, '%H:%M')
        f_end = datetime.strptime(slot_end, '%H:%M')
        if f_start <= start and f_end >= end:
            return True
    raise TimeIsNotAvailable


def get_emoji_for_status(status: str) -> str:
    """
    Get the emoji corresponding to the provided booking status.

    Args:
        status (str): The booking status.

    Returns:
        str: The emoji corresponding to the booking status.
    """
    statuses = {
        _('pending'): '🟡',
        _('confirmed'): '🟢',
        _('canceled'): '🔴',
        _('completed'): '🔵',
    }
    return statuses.get(status)


def generate_password() -> str:
    """
    Generate a random password consisting of 8 characters.

    Returns:
        str: The randomly generated password.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))


def generate_verification_code() -> str:
    """
    Generate a random verification code to confirm identity.

    Returns:
        str: The randomly generated verification code consisting
         of 6 characters.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))


def check_verification_code(source_code: str, user_code: str) -> bool:
    """
    Compare the provided verification codes.

    Args:
        source_code (str): The original verification code.
        user_code (str): The user-entered verification code.

    Returns:
        bool: True if the user-entered code matches the original code,
         False otherwise.

    Raises:
        CodesCompareError: If the codes do not match.
    """
    if source_code == user_code:
        return True
    raise CodesCompareError


def vk_notify(is_admin: bool, created: bool, **kwargs) -> None:
    """
    Send a notification to VK (Vkontakte) using the provided data.

    Args:
        is_admin (bool): Indicates whether the notification is for an admin.
        created (bool): Indicates whether the booking was just created.
        **kwargs: Additional keyword arguments containing
                    user and booking information.

    Returns:
        None

    Example Usage:
        vk_notify(True, True, user_info=user_data, data=booking_data)
    """
    f_phone = kwargs.get('f_phone')
    phone = f_phone if f_phone else kwargs.get('phone')
    via = _('Telegram Bot')
    data = {
        'pk': kwargs.get('pk'),
        'client': kwargs.get('username'),
        'date': kwargs.get('date'),
        'start': kwargs.get('start'),
        'end': kwargs.get('end'),
        'bikes': kwargs.get('bikes'),
        'phone': phone,
        'status': kwargs.get('status'),
    }
    send_vk_notify.delay(via, created, data, is_admin)


def mail_notify(action: str, **kwargs) -> None:
    """
    Send email notifications based on the specified action.

    Args:
        action (str): The action for which to send the notification.
        **kwargs: Additional keyword arguments to pass to the email
         sending functions.

    Returns:
        None
    """
    match action:
        case a if a == 'booking_details':
            book_mail.send_booking_details.delay(**kwargs)
        case a if a == 'confirm_msg':
            book_mail.send_confirm_message.delay(**kwargs)
        case a if a == 'cancel_msg':
            book_mail.send_cancel_message.delay(**kwargs)
        case a if a == 'self_cancel':
            book_mail.send_cancel_self_message.delay(**kwargs)
        case a if a == 'hello_msg':
            user_mail.send_hello_msg.delay(**kwargs)
        case a if a == 'verification_code':
            user_mail.send_verification_code.delay(**kwargs)
        case a if a == 'recover':
            user_mail.send_recover_message.delay(**kwargs)
        case a if a == 'booking_edit':
            book_mail.send_edit_booking_message.delay(**kwargs)
        case a if a == 'self_booking_edit':
            book_mail.send_self_edit_booking_message.delay(**kwargs)


def json_filter(data: dict) -> dict:
    """
    Filter out instances of ReplyKeyboardMarkup from a dictionary.

    Args:
        data (dict): The input dictionary to filter.

    Returns:
        dict: A new dictionary with instances of ReplyKeyboardMarkup removed.
    """
    return {
        key: value for key, value in data.items()
        if not isinstance(value, ReplyKeyboardMarkup)
    }
