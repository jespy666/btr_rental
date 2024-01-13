from datetime import datetime

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
        try:
            booked_seconds = self.get_booked_seconds(booked_slots)
            available_slots = self.get_available_slots(booked_seconds)
            return available_slots
        except ValidationError:
            return []


check_available_field_as = sync_to_async(check_available_field)
create_account_as = sync_to_async(create_user_by_bot)
make_foreign_book_as = sync_to_async(create_booking_by_admin)
check_booking_info_as = sync_to_async(check_booking_info)
change_booking_status_as = sync_to_async(change_booking_status)
