from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from asgiref.sync import sync_to_async

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


check_available_field_as = sync_to_async(check_available_field)
create_account_as = sync_to_async(create_user_by_bot)
