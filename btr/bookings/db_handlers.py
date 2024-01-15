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





#
#
# class LoadCalc:
#
#     FRIDAY = 5
#     ORDINARY_DAY_HOURS = 6
#     WEEKEND_DAY_HOURS = 8
#
#     def __init__(self, calendar: list, year: int, month: int):
#         self.calendar = calendar
#         self.year = year
#         self.month = month
#
#     def get_day_load(self, date: str) -> int:
#         """Get the workload of given date as a percentage"""
#         if date.split('-')[-1] == '0':
#             return -1
#         bookings = (Booking.objects.filter(booking_date=date)
#                     .exclude(status='canceled'))
#         book_time = 0
#         for booking in bookings:
#             start_time = booking.start_time
#             end_time = booking.end_time
#             start = datetime.combine(datetime.today(), start_time)
#             end = datetime.combine(datetime.today(), end_time)
#             duration = (end - start).seconds // 3600
#             book_time += duration
#         if self.is_weekend(date):
#             return int((book_time / self.WEEKEND_DAY_HOURS) * 100)
#         return int((book_time / self.ORDINARY_DAY_HOURS) * 100)
#
#     def get_week_load(self, week: list) -> list:
#         """Distribute load on week"""
#         week_load = []
#         for day in week:
#             date = f'{self.year}-{self.month}-{day}'
#             slots = SlotsFinder(date).find_available_slots()
#             day_load = (day, self.get_day_load(date), slots)
#             week_load.append(day_load)
#         return week_load
#
#     def is_weekend(self, date: str) -> bool:
#         """Check if day is a weekend"""
#         f_date = datetime.strptime(date, "%Y-%m-%d")
#         return f_date.weekday() >= self.FRIDAY
#
#     def get_month_load(self):
#         """Calculate full month load"""
#         return [self.get_week_load(week) for week in self.calendar]
#
#


#
# create_user_by_bot_as = sync_to_async(create_user_by_bot)
# check_user_exist_as = sync_to_async(check_user_exist)
# # create_booking_by_bot_as = sync_to_async(create_booking_by_bot)
# create_booking_by_admin_as = sync_to_async(create_booking_by_admin)
# # check_available_field_as = sync_to_async(check_available_field)
# reset_user_password_as = sync_to_async(reset_user_password)
# check_booking_status_as = sync_to_async(check_booking_info)
# # change_booking_status_as = sync_to_async(change_booking_status)
