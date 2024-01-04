from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q

from btr.users.models import SiteUser
from btr.bookings.models import Booking
from btr.bookings.bot_handlers import calculate_time_interval
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
    """Function check user exist from database"""
    try:
        SiteUser.objects.get(email=email)
        return True
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist


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
        bookings = Booking.objects.filter(booking_date=date)
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


class SlotsFinder:

    ORDINARY_SLOTS = '16:00:00-22:00:00'
    WEEKEND_SLOTS = '10:00:00-18:00:00'
    FRIDAY = 5

    def __init__(self, date: str):
        self.date = date

    def is_weekend(self) -> bool:
        """Check if day is a weekend"""
        f_date = datetime.strptime(self.date, "%Y-%m-%d")
        return f_date.weekday() >= self.FRIDAY

    def get_booked_slots(self) -> list:
        """Get busy time ranges from db"""
        bookings = Booking.objects.filter(booking_date=self.date)
        return [f'{book.start_time}-{book.end_time}' for book in bookings]

    @staticmethod
    def get_booked_seconds(booked_slots: list) -> list:
        """Calculate booked ranges to seconds"""
        booked_seconds = []
        for slot in booked_slots:
            start, end = map(lambda x: int(x.replace(':', '')),
                             slot.split('-'))
            booked_seconds.append((start, end))
        return sorted(booked_seconds)

    def get_available_slots(self, booked_seconds: list):
        if self.is_weekend():
            total_start, total_end = map(lambda x: int(x.replace(':', '')),
                                         self.WEEKEND_SLOTS.split('-'))
        else:
            total_start, total_end = map(lambda x: int(x.replace(':', '')),
                                         self.ORDINARY_SLOTS.split('-'))
        free_slots = []
        last_end = total_start
        for start, end in booked_seconds:
            if start > last_end:
                free_slots.append((last_end, start))
            last_end = max(last_end, end)
        if last_end < total_end:
            free_slots.append((last_end, total_end))
        available_slots = [
            (
                f'{str(start)[:2]}:{str(start)[2:4]}',
                f'{str(end)[:2]}:{str(end)[2:4]}',
            )
            for start, end in free_slots if start != end
        ]
        return available_slots

    def find_available_slots(self) -> list:
        """Get list of available slots for view"""
        if self.date.split('-')[-1] == '0':
            return []
        booked_slots = self.get_booked_slots()
        booked_seconds = self.get_booked_seconds(booked_slots)
        available_slots = self.get_available_slots(booked_seconds)
        return available_slots

    async def find_available_slots_as(self) -> list:
        """Get list of available slots for bot"""
        get_booking_slots_as = sync_to_async(self.get_booked_slots)
        booked_slots = await get_booking_slots_as()
        booked_seconds = self.get_booked_seconds(booked_slots)
        available_slots = self.get_available_slots(booked_seconds)
        return available_slots


create_user_by_bot_as = sync_to_async(create_user_by_bot)
check_user_exist_as = sync_to_async(check_user_exist)
create_booking_by_bot_as = sync_to_async(create_booking_by_bot)
create_booking_by_admin_as = sync_to_async(create_booking_by_admin)
check_available_field_as = sync_to_async(check_available_field)
reset_user_password_as = sync_to_async(reset_user_password)
