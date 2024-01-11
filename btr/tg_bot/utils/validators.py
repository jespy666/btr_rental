import re

from .exceptions import (NameOverLengthError, InvalidEmailError,
                         InvalidPhoneError)


MAX_NAME_LENGTH = 40


def validate_name(name: str) -> bool:
    """Validate name or username length.
     Field can't be greater than 40 symbols"""
    if len(name) < MAX_NAME_LENGTH:
        return True
    else:
        raise NameOverLengthError


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    else:
        raise InvalidEmailError


def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number input"""
    pattern = r'^\+7\d{10}$'
    if re.match(pattern, phone_number):
        return True
    else:
        raise InvalidPhoneError
