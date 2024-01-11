from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from btr.users.models import SiteUser
from btr.bookings.models import Booking
from asgiref.sync import sync_to_async


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
        first_name=first_name,
        status='Newbie',
    )

    user.set_password(password)
    user.save()
    return password


def check_user_exist(email: str) -> bool:
    """Check user exist by email"""
    try:
        SiteUser.objects.get(email=email)
        return True
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist


# def create_booking_by_bot(user_data: dict) -> dict:
#     """User create booking yourself via tg bot"""
#     user_email = user_data.get('user_email')
#     user = SiteUser.objects.get(email=user_email)
#
#     date = user_data.get('book_date')
#     time = user_data.get('book_start_time')
#     hours = user_data.get('book_hours')
#     bike_count = user_data.get('bike_count')
#     # interval = calculate_time_interval(time, hours)
#     phone_number = get_phone_number(user_email)
#
#     booking = Booking.objects.create(
#         rider=user,
#         foreign_number=phone_number,
#         booking_date=date,
#         start_time=interval.get('start_time'),
#         end_time=interval.get('end_time'),
#         bike_count=bike_count,
#         status='pending',
#     )
#     booking.save()
#     return interval


def create_booking_by_admin(user_data: dict) -> None:
    """Admin create booking by rider phone number via tg bot.
    Booked to admin account"""
    user = SiteUser.objects.get(username='admin')
    phone = user_data.get('phone')
    date = user_data.get('date')
    start_time = user_data.get('start')
    end_time = user_data.get('end')
    bike_count = user_data.get('bikes')

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


def reset_user_password(user_email: str) -> str:
    """Set new random password to user by email"""
    user = SiteUser.objects.get(email=user_email)
    password = SiteUser.objects.make_random_password(length=8)
    user.set_password(password)
    user.save()
    return password


def check_booking_info(booking_id: str) -> dict:
    """Checking and return booking info by primary key"""
    booking = Booking.objects.get(pk=int(booking_id))
    return {
        'date': booking.booking_date,
        'start': booking.start_time,
        'end': booking.end_time,
        'status': booking.status,
    }


# def change_booking_status(booking_id: str, status: str) -> str:
#     """Change booking status by primary key"""
#     booking = Booking.objects.get(pk=int(booking_id))
#     old_status = booking.status
#     if old_status == status:
#         raise SameStatusSelected
#     booking.status = status
#     booking.save()
#     return old_status


class LoadCalc:

    FRIDAY = 5
    ORDINARY_DAY_HOURS = 6
    WEEKEND_DAY_HOURS = 8

    def __init__(self, calendar: list, year: int, month: int):
        self.calendar = calendar
        self.year = year
        self.month = month

    def get_day_load(self, date: str) -> int:
        """Get the workload of given date as a percentage"""
        if date.split('-')[-1] == '0':
            return -1
        bookings = (Booking.objects.filter(booking_date=date)
                    .exclude(status='canceled'))
        book_time = 0
        for booking in bookings:
            start_time = booking.start_time
            end_time = booking.end_time
            start = datetime.combine(datetime.today(), start_time)
            end = datetime.combine(datetime.today(), end_time)
            duration = (end - start).seconds // 3600
            book_time += duration
        if self.is_weekend(date):
            return int((book_time / self.WEEKEND_DAY_HOURS) * 100)
        return int((book_time / self.ORDINARY_DAY_HOURS) * 100)

    def get_week_load(self, week: list) -> list:
        """Distribute load on week"""
        week_load = []
        for day in week:
            date = f'{self.year}-{self.month}-{day}'
            slots = SlotsFinder(date).find_available_slots()
            day_load = (day, self.get_day_load(date), slots)
            week_load.append(day_load)
        return week_load

    def is_weekend(self, date: str) -> bool:
        """Check if day is a weekend"""
        f_date = datetime.strptime(date, "%Y-%m-%d")
        return f_date.weekday() >= self.FRIDAY

    def get_month_load(self):
        """Calculate full month load"""
        return [self.get_week_load(week) for week in self.calendar]





create_user_by_bot_as = sync_to_async(create_user_by_bot)
check_user_exist_as = sync_to_async(check_user_exist)
# create_booking_by_bot_as = sync_to_async(create_booking_by_bot)
create_booking_by_admin_as = sync_to_async(create_booking_by_admin)
# check_available_field_as = sync_to_async(check_available_field)
reset_user_password_as = sync_to_async(reset_user_password)
check_booking_status_as = sync_to_async(check_booking_info)
# change_booking_status_as = sync_to_async(change_booking_status)
