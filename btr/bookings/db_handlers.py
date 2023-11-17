from btr.users.models import SiteUser
from asgiref.sync import sync_to_async


def create_user_by_bot(user_data: dict):
    username = user_data.get('username')
    first_name = user_data.get('first_name')
    email = user_data.get('email')
    phone_number = user_data.get('phone_number')

    user = SiteUser(
        username=username,
        first_name=first_name,
        email=email,
        phone_number=phone_number,
    )

    user.save()


create_user_by_bot_as = sync_to_async(create_user_by_bot)
