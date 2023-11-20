from django.core.exceptions import ObjectDoesNotExist

from btr.users.models import SiteUser
from btr.bookings.time_handler import calculate_time_interval
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


def check_user_exist(email):
    try:
        return SiteUser.objects.get(email=email)
    except ObjectDoesNotExist:
        return None


def create_booking_by_bot(book_data: dict):
    date = book_data.get('book_date')
    time = book_data.get('book_start_time')
    hours = book_data.get('book_hours')
    interval = calculate_time_interval(time, hours)


create_user_by_bot_as = sync_to_async(create_user_by_bot)
