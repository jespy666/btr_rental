import os
import secrets
import string
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiogram.types import ReplyKeyboardMarkup

from django.utils.translation import gettext as _

from .exceptions import TimeIsNotAvailable, CodesCompareError
from btr.tasks.admin import send_vk_notify
from btr.tasks import bookings as book_mail
from btr.tasks import users as user_mail


def check_admin_access(user_id: int) -> bool:
    """Check current user as admin"""
    load_dotenv()
    admin_ids = os.getenv('TG_ADMIN_IDS')
    return user_id in eval(admin_ids)


def extract_start_times(intervals: list) -> list:
    """Get all available start times to bot buttons"""
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
    """Returned date with month name"""
    date_object = datetime.strptime(date, '%Y-%m-%d')
    return date_object.strftime('%Y-%B-%d')


def extract_hours(slots: list, start_time: str) -> list:
    """Get choices list of available hours"""
    for start, end in slots:
        start_hours = int(start.split(':')[0])
        end_hours = int(end.split(':')[0])
        book_hours = int(start_time.split(':')[0])
        if start_hours <= book_hours < end_hours:
            available_hours = end_hours - book_hours
            return [str(i) for i in range(1, available_hours + 1)]


def get_slots_for_bot_view(slots: list) -> str:
    """Show free booking slots for given date"""
    bot_view_slots = ''
    for slot in slots:
        bot_view_slots += f'{slot[0]}-{slot[1]}\n'
    return bot_view_slots


def check_available_start_time(start_time: str, slots: list) -> bool:
    """Check given time in free slot"""
    for slot_start, slot_end in slots:
        if slot_start <= start_time < slot_end:
            return True
    raise TimeIsNotAvailable


def get_end_time(start_time: str, hours: str) -> str:
    """Calculate end time by hours"""
    start = datetime.strptime(start_time, "%H:%M")
    end = start + timedelta(hours=int(hours))
    return end.strftime('%H:%M')


def get_hours(start: str, end: str) -> str:
    """Calculate timedelta in hours"""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    delta = end_time - start_time
    hours = int(delta.total_seconds() // 3600)
    return str(hours)


def check_available_hours(start_time: str, hours: str, slots: list) -> bool:
    """Available time range validator"""
    start = datetime.strptime(start_time, '%H:%M')
    end = start + timedelta(hours=int(hours))
    for slot_start, slot_end in slots:
        f_start = datetime.strptime(slot_start, '%H:%M')
        f_end = datetime.strptime(slot_end, '%H:%M')
        if f_start <= start and f_end >= end:
            return True
    raise TimeIsNotAvailable


def get_emoji_for_status(status: str) -> str:
    """Get tg emoji equal booking status"""
    statuses = {
        _('pending'): '🟡',
        _('confirmed'): '🟢',
        _('canceled'): '🔴',
        _('completed'): '🔵',
    }
    return statuses.get(status)


def generate_password() -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))


def generate_verification_code() -> str:
    """Generate random code to confirm personality"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))


def check_verification_code(source_code: str, user_code: str) -> bool:
    """Compare verification codes"""
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
    return {
        key: value for key, value in data.items()
        if not isinstance(value, ReplyKeyboardMarkup)
    }
