from datetime import datetime, date
import re

from btr.bookings.bot_exceptions import InvalidTimeFormat, InvalidDateFormat, \
    WrongBikeCount, InvalidEmailFormat, DateInPastException

MIN_BIKES_COUNT = 1
MAX_BIKES_COUNT = 4
MIN_HOURS = 1
MAX_HOURS = 24
MAX_FIRST_NAME_LENGTH = 40


def validate_bike_quantity(count: str) -> bool:
    """Validate bike's count input. Count must be in 1-4 pcs"""
    try:
        int(count)
    except ValueError:
        raise WrongBikeCount
    if int(count) in set(range(MIN_BIKES_COUNT, MAX_BIKES_COUNT + 1)):
        return True
    raise WrongBikeCount


def validate_email(email: str) -> bool:
    """Validate email input"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    else:
        raise InvalidEmailFormat


def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number input"""
    pattern = r'^\+7\d{10}$'
    if re.match(pattern, phone_number):
        return True
    else:
        raise ValueError


def validate_date(date_str: str) -> bool:
    """Validate date input. The date cannot be in the past"""
    try:
        input_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = date.today()
        if input_date >= today:
            return True
        else:
            raise DateInPastException
    except ValueError:
        raise InvalidDateFormat


def validate_time(time: str) -> bool:
    """Validate time input format"""
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
    if re.match(pattern, time):
        return True
    else:
        raise InvalidTimeFormat


def validate_time_range(start_time: str, end_time: str) -> bool:
    """Check for start time must be less than end time"""
    format_str = '%H:%M'
    start = datetime.strptime(start_time, format_str)
    end = datetime.strptime(end_time, format_str)
    if start < end:
        return True
    else:
        raise ValueError


def validate_hours(hours: str) -> bool:
    """Validate hours count. Counter must be in 1-24"""
    if MIN_HOURS <= int(hours) <= MAX_HOURS:
        return True
    else:
        raise ValueError


def validate_first_name(first_name: str) -> bool:
    """Validate first name length. Field can't be greater than 40 symbols"""
    if len(first_name) < MAX_FIRST_NAME_LENGTH:
        return True
    else:
        raise ValueError
