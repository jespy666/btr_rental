import re
from datetime import datetime, date

from django.utils.translation import gettext as _

from ..utils import exceptions as e


MAX_NAME_LENGTH = 40
MIN_BIKES_COUNT = 1
MAX_BIKES_COUNT = 4


def validate_name(name: str) -> bool:
    """
    Validate the length of a name or username.

    Args:
        name (str): The name or username to validate.

    Returns:
        bool: True if the length of the name is less than 40 characters,
         False otherwise.

    Raises:
        NameOverLength: If the length of the name exceeds 40 characters.
    """
    if len(name) < MAX_NAME_LENGTH:
        return True
    else:
        raise e.NameOverLength


def validate_email(email: str) -> bool:
    """
    Validate the format of an email address.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address has a valid format, False otherwise.

    Raises:
        InvalidEmailFormat: If the email address does not have a valid format.
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    else:
        raise e.InvalidEmailFormat


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate the format of a phone number.

    Args:
        phone_number (str): The phone number to validate.

    Returns:
        bool: True if the phone number has a valid format, False otherwise.

    Raises:
        InvalidPhoneFormat: If the phone number does not have a valid format.
    """
    pattern = r'^\+7\d{10}$'
    if re.match(pattern, phone_number):
        return True
    else:
        raise e.InvalidPhoneFormat


def validate_bike_quantity(count: str) -> bool:
    """
    Validate the input for bike quantity.

    Args:
        count (str): The input string representing the bike count.

    Returns:
        bool: True if the bike count is within the valid range,
         False otherwise.

    Raises:
        WrongBikesCount: If the input is not a valid integer or if
         it's not within the range of 1 to 4.
    """
    try:
        int(count)
    except ValueError:
        raise e.WrongBikesCount
    if int(count) in set(range(MIN_BIKES_COUNT, MAX_BIKES_COUNT + 1)):
        return True
    raise e.WrongBikesCount


def validate_date(date_str: str) -> bool:
    """
    Validate the input date.

    Args:
        date_str (str): The input date string in the format 'YYYY-MM-DD'.

    Returns:
        bool: True if the date is valid and not in the past, False otherwise.

    Raises:
        InvalidDate: If the input date string is not in the correct format.
        PastTense: If the input date is in the past.
    """
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
    """
    Validate the format of a time string.

    Args:
        time (str): The time string to validate.

    Returns:
        bool: True if the time string has a valid format, False otherwise.

    Raises:
        InvalidTimeFormat: If the time string does not have a valid format.
    """
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
    if re.match(pattern, time):
        return True
    else:
        raise e.InvalidTimeFormat


def validate_time_range(start_time: str, end_time: str) -> bool:
    """
    Validate the time range.

    Args:
        start_time (str): The start time string in the format 'HH:MM'.
        end_time (str): The end time string in the format 'HH:MM'.

    Returns:
        bool: True if the start time is earlier than the end time,
         False otherwise.

    Raises:
        EndBiggerStart: If the end time is not greater than the start time.
    """
    format_str = '%H:%M'
    start = datetime.strptime(start_time, format_str)
    end = datetime.strptime(end_time, format_str)
    if start < end:
        return True
    raise e.EndBiggerStart


def validate_pks(pk: str, bookings_id: list) -> bool:
    """
    Validate if an ID is included in the list of booking IDs.

    Args:
        pk (str): The ID to check.
        bookings_id (list): List of booking IDs.

    Returns:
        bool: True if the ID is included in the list, False otherwise.

    Raises:
        NotExistedId: If the ID is not included in the list.
    """
    if pk in bookings_id:
        return True
    raise e.NotExistedId


def validate_id(pk: str) -> bool:
    """
    Validate the format of an ID.

    Args:
        pk (str): The ID to validate.

    Returns:
        bool: True if the ID has a valid format, False otherwise.

    Raises:
        InvalidIDFormat: If the ID does not have a valid format.
    """
    try:
        int(pk)
        return True
    except ValueError:
        raise e.InvalidIDFormat


def validate_hours(hours: str) -> bool:
    """
    Validate the format of hours.

    Args:
        hours (str): The hours to validate.

    Returns:
        bool: True if the hours have a valid format, False otherwise.

    Raises:
        WrongHoursFormat: If the hours do not have a valid format.
    """
    try:
        int(hours)
        return True
    except ValueError:
        raise e.WrongHoursFormat


def validate_status(status: str) -> bool:
    """
    Validate the status keyboard input.

    Args:
        status (str): The status input to validate.

    Returns:
        bool: True if the status input is valid, False otherwise.

    Raises:
        WrongStatus: If the status input is not valid.
    """
    if status in (_('pending'), _('confirmed'), _('canceled')):
        return True
    raise e.WrongStatus
