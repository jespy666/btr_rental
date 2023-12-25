import math
from datetime import datetime, timedelta, date

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q

from btr.users.models import SiteUser
from btr.bookings.models import Booking
from btr.bookings.bot_handlers import calculate_time_interval
from asgiref.sync import sync_to_async


FRIDAY = 5
ORDINARY_DAY_HOURS = 6
WEEKEND_DAY_HOURS = 8


def create_user_by_bot(user_data: dict) -> str:
    """User create an account via tg bot"""
    username = user_data.get('username')
    first_name = user_data.get('first_name')
    email = user_data.get('email')
    phone_number = user_data.get('phone_number')

    password = SiteUser.objects.make_random_password(length=8)

    user = SiteUser.objects.create(
        username=username,
        email=email,
        phone_number=phone_number,
        first_name=first_name
    )

    user.set_password(password)
    user.save()
    return password


def check_user_exist(email: str) -> bool:
    """Function check user exist from database"""
    try:
        SiteUser.objects.get(email=email)
        return True
    except ObjectDoesNotExist:
        raise NameError


def create_booking_by_bot(user_data: dict) -> dict:
    """User create booking yourself via tg bot"""
    user_email = user_data.get('user_email')
    user = SiteUser.objects.get(email=user_email)

    date = user_data.get('book_date')
    time = user_data.get('book_start_time')
    hours = user_data.get('book_hours')
    bike_count = user_data.get('bike_count')
    interval = calculate_time_interval(time, hours)
    phone_number = get_phone_number(user_email)

    booking = Booking.objects.create(
        rider=user,
        foreign_number=phone_number,
        booking_date=date,
        start_time=interval.get('start_time'),
        end_time=interval.get('end_time'),
        bike_count=bike_count,
        status='pending',
    )
    booking.save()
    return interval


def create_booking_by_admin(user_data: dict) -> None:
    """Admin create booking by rider phone number via tg bot.
    Booked to admin account"""
    user = SiteUser.objects.get(username='admin')
    phone = user_data.get('foreign_phone')
    date = user_data.get('foreign_date')
    start_time = user_data.get('foreign_start')
    end_time = user_data.get('foreign_end')
    bike_count = user_data.get('bikes_num')

    booking = Booking.objects.create(
        rider=user,
        foreign_number=phone,
        booking_date=date,
        start_time=start_time,
        end_time=end_time,
        bike_count=bike_count,
        status='confirmed'
    )
    booking.save()


def get_phone_number(user_email: str) -> str:
    """Find user phone number by email from database"""
    try:
        user = SiteUser.objects.get(email=user_email)
        return user.phone_number
    except ObjectDoesNotExist:
        raise NameError


def check_available_field(user_input: str) -> bool:
    """Function checks the availability of fields in the database"""
    try:
        user = SiteUser.objects.get(
            Q(username=user_input) |
            Q(email=user_input) |
            Q(phone_number=user_input)
        )
        return False
    except ObjectDoesNotExist:
        return True
    except MultipleObjectsReturned:
        return False


def reset_user_password(user_email: str) -> str:
    """Set new random password to user by email"""
    user = SiteUser.objects.get(email=user_email)
    password = SiteUser.objects.make_random_password(length=8)
    user.set_password(password)
    user.save()
    return password


def get_month_load(calendar: list, year: int, month: int) -> list:
    """Get the workload of each day in month as a percentage"""
    percentage_load = []
    for week in calendar:
        day_load = [
            (day, get_day_load(f'{year}-{month}-{day}')) for day in week
        ]
        percentage_load.append(day_load)
    return percentage_load


def get_day_load(current_date: str) -> int:
    """Get the workload of current day as a percentage"""
    if current_date.split('-')[-1] == '0':
        return -1
    bookings = Booking.objects.filter(
        booking_date=current_date,
    )
    date_format = datetime.strptime(current_date, "%Y-%m-%d").date()
    book_time = 0
    for booking in bookings:
        start_time = booking.start_time
        end_time = booking.end_time
        start = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        duration = (end - start).seconds // 3600
        book_time += duration
    if is_weekend(date_format):
        return int((book_time / WEEKEND_DAY_HOURS) * 100)
    return int((book_time / ORDINARY_DAY_HOURS) * 100)


def is_weekend(current_date: datetime.date) -> bool:
    """Check if day is a weekend"""
    return current_date.weekday() >= FRIDAY


create_user_by_bot_as = sync_to_async(create_user_by_bot)
check_user_exist_as = sync_to_async(check_user_exist)
create_booking_by_bot_as = sync_to_async(create_booking_by_bot)
create_booking_by_admin_as = sync_to_async(create_booking_by_admin)
check_available_field_as = sync_to_async(check_available_field)
reset_user_password_as = sync_to_async(reset_user_password)
