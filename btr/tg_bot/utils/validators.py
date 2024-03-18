import re
from datetime import datetime, date

from django.utils.translation import gettext as _

from ..utils import exceptions as e


MAX_NAME_LENGTH = 40
MIN_BIKES_COUNT = 1
MAX_BIKES_COUNT = 4


def validate_name(name: str) -> bool:
    """Validate name or username length.
     Field can't be greater than 40 symbols"""
    if len(name) < MAX_NAME_LENGTH:
        return True
    else:
        raise e.NameOverLength


def validate_email(email: str) -> bool:
    """Validate emails format"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    else:
        raise e.InvalidEmailFormat


def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number input"""
    pattern = r'^\+7\d{10}$'
    if re.match(pattern, phone_number):
        return True
    else:
        raise e.InvalidPhoneFormat


def validate_bike_quantity(count: str) -> bool:
    """Validate bike's count input. Count must be in 1-4 pcs"""
    try:
        int(count)
    except ValueError:
        raise e.WrongBikesCount
    if int(count) in set(range(MIN_BIKES_COUNT, MAX_BIKES_COUNT + 1)):
        return True
    raise e.WrongBikesCount


def validate_date(date_str: str) -> bool:
    """Validate date input. The date cannot be in the past"""
    try:
        input_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = date.today()
        if input_date >= today:
            return True
        else:
            raise e.PastTense
    except ValueError:
        raise e.InvalidDate


def validate_time(time: str) -> bool:
    """Validate time input format"""
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
    if re.match(pattern, time):
        return True
    else:
        raise e.InvalidTimeFormat


def validate_time_range(start_time: str, end_time: str) -> bool:
    """Check for start time must be less than end time"""
    format_str = '%H:%M'
    start = datetime.strptime(start_time, format_str)
    end = datetime.strptime(end_time, format_str)
    if start < end:
        return True
    raise e.EndBiggerStart


def validate_pks(pk: str, bookings_id: list) -> bool:
    """Checking whether an ID is included in the list"""
    if pk in bookings_id:
        return True
    raise e.NotExistedId


def validate_id(pk: str) -> bool:
    """Validate id format"""
    try:
        int(pk)
        return True
    except ValueError:
        raise e.InvalidIDFormat


def validate_hours(hours: str) -> bool:
    """Validate hours format"""
    try:
        int(hours)
        return True
    except ValueError:
        raise e.WrongHoursFormat


def validate_status(status: str) -> bool:
    """Validate status keyboard input"""
    if status in (_('pending'), _('confirmed'), _('canceled')):
        return True
    raise e.WrongStatus
