from django.core.exceptions import ObjectDoesNotExist

from btr.users.models import SiteUser
from btr.bookings.models import Booking
from btr.bookings.bot_handlers import calculate_time_interval
from asgiref.sync import sync_to_async


def create_user_by_bot(user_data: dict):
    username = user_data.get('username')
    first_name = user_data.get('first_name')
    email = user_data.get('email')
    phone_number = user_data.get('phone_number')

    password = SiteUser.objects.make_random_password(length=8)

    user = SiteUser.objects.create(username=username, email=email,
                                   phone_number=phone_number,
                                   first_name=first_name)

    user.set_password(password)
    user.save()

    return email, first_name, password


def check_user_exist(email: str):
    try:
        SiteUser.objects.get(email=email)
        return True
    except ObjectDoesNotExist:
        raise NameError


def create_booking_by_bot(user_data: dict):
    user_email = user_data.get('user_email')
    user = SiteUser.objects.get(email=user_email)

    date = user_data.get('book_date')
    time = user_data.get('book_start_time')
    hours = user_data.get('book_hours')
    bike_count = user_data.get('bike_count')
    interval = calculate_time_interval(time, hours)
    if interval:
        booking = Booking.objects.create(
            rider=user,
            booking_date=date,
            start_time=interval.get('start_time'),
            end_time=interval.get('end_time'),
            bike_count=bike_count,
            status='pending',
        )
        booking.save()
        return interval, interval.get('end_time')
    else:
        raise ValueError


def create_booking_by_admin(user_data: dict):
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


create_user_by_bot_as = sync_to_async(create_user_by_bot)
check_user_exist_as = sync_to_async(check_user_exist)
create_booking_by_bot_as = sync_to_async(create_booking_by_bot)
create_booking_by_admin_as = sync_to_async(create_booking_by_admin)
