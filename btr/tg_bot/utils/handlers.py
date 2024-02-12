import secrets
import string
from datetime import datetime, timedelta
from django.utils.translation import gettext as _

from dotenv import load_dotenv
import os

from .exceptions import TimeIsNotAvailableError, CompareCodesError


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
    raise TimeIsNotAvailableError


def get_end_time(start_time: str, hours: str) -> str:
    """Calculate end time by hours"""
    start = datetime.strptime(start_time, "%H:%M")
    end = start + timedelta(hours=int(hours))
    return end.strftime('%H:%M')


def check_available_hours(start_time: str, hours: str, slots: list) -> bool:
    """Check all user time interval in free slot"""
    start = datetime.strptime(start_time, '%H:%M')
    end = start + timedelta(hours=int(hours))
    for slot_start, slot_end in slots:
        f_start = datetime.strptime(slot_start, '%H:%M')
        f_end = datetime.strptime(slot_end, '%H:%M')
        if f_start <= start and f_end >= end:
            return True
    raise TimeIsNotAvailableError


def get_emoji_for_status(status: str) -> str:
    """Get tg emoji equal booking status"""
    statuses = {
        _('pending'): '🟡',
        _('confirmed'): '🟢',
        _('canceled'): '🔴',
        _('completed'): '🔵',
    }
    return statuses.get(status)


def generate_verification_code() -> str:
    """Generate random code to confirm personality"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))


def check_verification_code(source_code: str, user_code: str) -> bool:
    """Compare verification codes"""
    if source_code == user_code:
        return True
    raise CompareCodesError
