from datetime import datetime
from typing import Union, Tuple, Optional

from django.core.exceptions import (ObjectDoesNotExist,
                                    MultipleObjectsReturned,
                                    ValidationError)
from django.db.models import Q
from asgiref.sync import sync_to_async

from btr.bookings.models import Booking
from btr.tg_bot.utils.exceptions import SameStatusSelectedError
from btr.users.models import SiteUser


def check_user_exist(email: str) -> bool:
    """Check user exist by email"""
    try:
        SiteUser.objects.get(email=email)
        return True
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist


def check_available_field(user_input: str) -> bool:
    """Checks availability of field"""
    try:
        SiteUser.objects.get(
            Q(username=user_input) |
            Q(email=user_input) |
            Q(phone_number=user_input)
        )
        return False
    except ObjectDoesNotExist:
        return True
    except MultipleObjectsReturned:
        return False


def check_booking_info(booking_id: str) -> dict:
    """Checking and return booking info by primary key"""
    booking = Booking.objects.get(pk=int(booking_id))
    return {
        'date': booking.booking_date,
        'start': booking.start_time,
        'end': booking.end_time,
        'status': booking.status,
        'bikes': booking.bike_count,
        'phone': booking.rider.phone_number,
        'f_phone': booking.foreign_number,
        'r_username': booking.rider.username,
    }


def change_booking_status(booking_id: str, status: str) -> str:
    """Change booking status by primary key"""
    booking = Booking.objects.get(pk=int(booking_id))
    old_status = booking.status
    if old_status == status:
        raise SameStatusSelectedError
    booking.status = status
    booking.save()
    return old_status


def create_user_by_bot(reg_data: dict) -> str:
    """User create an account via tg bot"""
    username = reg_data.get('regusername')
    first_name = reg_data.get('regname')
    email = reg_data.get('regemail')
    phone_number = reg_data.get('regphone')
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


def create_booking_by_admin(book_data: dict) -> None:
    """Admin create booking by rider phone number via tg bot.
    Booked to admin account"""
    user = SiteUser.objects.get(username='admin')
    phone = book_data.get('outphone')
    date = book_data.get('outdate')
    start_time = book_data.get('outstart')
    end_time = book_data.get('outend')
    bike_count = book_data.get('outbikes')

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


def create_booking_by_bot(user_data: dict) -> str:
    """User create booking yourself via tg bot"""
    user_email = user_data.get('email')
    user = SiteUser.objects.get(email=user_email)

    date = user_data.get('date')
    start = user_data.get('start')
    end = user_data.get('end')
    bikes = user_data.get('bikes')
    phone_number = get_phone_number(user_email)

    booking = Booking.objects.create(
        rider=user,
        foreign_number=phone_number,
        booking_date=date,
        start_time=start,
        end_time=end,
        bike_count=bikes,
        status='pending',
    )
    booking.save()
    return booking.pk


def get_phone_number(user_email: str) -> str:
    """Find user phone number by email from database"""
    try:
        user = SiteUser.objects.get(email=user_email)
        return user.phone_number
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist


def reset_user_password(user_email: str) -> str:
    """Set new random password to user by email"""
    user = SiteUser.objects.get(email=user_email)
    password = SiteUser.objects.make_random_password(length=8)
    user.set_password(password)
    user.save()
    return password


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
        bookings = (Booking.objects.filter(booking_date=self.date)
                    .exclude(status='canceled'))
        return [f'{book.start_time}-{book.end_time}' for book in bookings]

    def get_booked_slots_for_edit(self, excluded_slot: tuple) -> list:
        """Get busy time ranges exclude current range"""
        exc_start, exc_end = excluded_slot
        bookings = (Booking.objects.filter(booking_date=self.date)
                    .exclude(status='canceled'))
        return [f'{book.start_time}-{book.end_time}' for book in bookings if
                (book.start_time >= exc_end or book.end_time <= exc_start)]

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

    def find_available_slots(
            self,
            excluded_slot: Union[
                None,
                Tuple[Optional[datetime.time], Optional[datetime.time]]
            ] = None) -> list:
        """Get list of available slots for view"""
        if self.date.split('-')[-1] == '0':
            return []
        if not excluded_slot:
            booked_slots = self.get_booked_slots()
        else:
            booked_slots = self.get_booked_slots_for_edit(excluded_slot)
        booked_seconds = self.get_booked_seconds(booked_slots)
        available_slots = self.get_available_slots(booked_seconds)
        return available_slots

    async def find_available_slots_as(self) -> list:
        """Get list of available slots for bot"""
        get_booking_slots_as = sync_to_async(self.get_booked_slots)
        booked_slots = await get_booking_slots_as()
        try:
            booked_seconds = self.get_booked_seconds(booked_slots)
            available_slots = self.get_available_slots(booked_seconds)
            return available_slots
        except ValidationError:
            return []


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


check_available_field_as = sync_to_async(check_available_field)
check_user_exist_as = sync_to_async(check_user_exist)
create_account_as = sync_to_async(create_user_by_bot)
make_foreign_book_as = sync_to_async(create_booking_by_admin)
create_booking_as = sync_to_async(create_booking_by_bot)
check_booking_info_as = sync_to_async(check_booking_info)
change_booking_status_as = sync_to_async(change_booking_status)
reset_user_password_as = sync_to_async(reset_user_password)
