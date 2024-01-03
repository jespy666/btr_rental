from datetime import datetime, timedelta
import secrets
import string

from .bot_exceptions import BusyDayException, TimeIsNotAvailable


def calculate_time_interval(start_time: str, hours: str) -> dict | None:
    """Calculate end time by hours"""
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(hours=int(hours))
        time_interval = {
            'start_time': start.strftime('%H:%M'),
            'end_time': end.strftime('%H:%M'),
        }
        return time_interval
    except ValueError:
        return None


def generate_verification_code() -> str:
    """Generate random code to confirm personality"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))


def check_verification_code(source_code: str, user_code: str) -> bool:
    """Check that the verification codes match"""
    if source_code == user_code:
        return True
    else:
        raise ValueError


async def get_free_slots_for_bot_view(date: str) -> str:
    """Show free booking slots for given date"""
    from .db_handlers import SlotsFinder
    slots = SlotsFinder(date)
    available_slots = await slots.find_available_slots_as()
    if not available_slots:
        raise BusyDayException
    bot_view_slots = ''
    for slot in available_slots:
        bot_view_slots += f'{slot[0]}-{slot[1]}\n'
    return bot_view_slots


def check_available_start_time(start_time: str, available_slots: str) -> bool:
    """Check given time in free slot"""
    slots = available_slots.strip().split('\n')
    for slot in slots:
        slot_start, slot_end = slot.split('-')
        if slot_start <= start_time < slot_end:
            return True
    raise TimeIsNotAvailable


def check_available_hours(start_time: str, hours: str, available_slots: str) \
        -> bool:
    """Check all user time interval in free slot"""
    slots = available_slots.strip().split('\n')
    start = datetime.strptime(start_time, '%H:%M')
    end = start + timedelta(hours=int(hours))
    for slot in slots:
        slot_start, slot_end = slot.split('-')
        f_start = datetime.strptime(slot_start, '%H:%M')
        f_end = datetime.strptime(slot_end, '%H:%M')
        if f_start <= start and f_end >= end:
            return True
    raise TimeIsNotAvailable
