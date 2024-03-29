import os
from dotenv import load_dotenv
from django.utils.translation import gettext as _

from ..vk import SendBookingNotification
from ..celery import app


@app.task
def send_vk_notify(via: str, created: bool, data: dict,
                   is_admin=False) -> None:
    """
    Send a message in VK after successfully booking or changing status.

    Args:
        via (str): The source of the notification (e.g., 'Admin panel').
        created (bool): Indicates whether the booking was just created.
        data (dict): Dictionary containing booking details.
        is_admin (bool, optional): Indicates if the user is an admin.
         Defaults to False.

    Returns:
        None

    Example data values:
        'pk' (str): Booking primary key (e.g '123')
        'client' (str): Rider username (e.g. 'john_doe')
        'phone' (str): Rider phone number (e.g. '+1234567890')
        'date' (str): Booking day (e.g. '%Y-%m-%d': '2024-03-29' as string)
        'start' (str): Booking start time (e.g. '10:00')
        'end' (str): Booking end time (e.g. '11:00')
        'bikes' (str): Booking bikes count as string (e.g. '2')
        'status' (str): Booking status (e.g. 'confirmed')
        'email' (str): Rider email (e.g. 'john@example.com')
    """
    load_dotenv()
    user_id = os.getenv('VK_ADMIN_ID')
    access_token = os.getenv('VK_BTR_KEY')
    vk = SendBookingNotification(user_id, access_token)
    status = data.get('status')
    username = _(
        'User with username {client}'
    ).format(client=data.get('client'))
    client = _(' {client}').format(client=data.get('client'))
    f_client = _('Foreign client')
    foreign_client = _(' {client}').format(client=f_client) if\
        data.get('client') == 'admin' else f" {data.get('client')}"
    emoji = {
        _('pending'): '🟡🟡🟡',
        _('confirmed'): '🟢🟢🟢',
        _('canceled'): '🔴🔴🔴'
    }
    if created:
        msg = _(
            '#{pk} 🆕\n\n'
            '{is_admin} just {is_self} for a rental{is_user} '
            'via {via}!\n\n'
            'Client\'s phone: {phone}\n\n'
            'Booking details:\n'
            '➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
            '📅  {date}\n'
            '🕒  {start} - {end}\n'
            '🏍 {bikes} bike(s)'
        ).format(
            pk=data.get('pk'),
            is_admin=_('Admin') if is_admin else username,
            is_self=_('sign up') if is_admin else _('signed up'),
            is_user=foreign_client if is_admin else '',
            via=via,
            phone=data.get('phone'),
            date=data.get('date'),
            start=data.get('start'),
            end=data.get('end'),
            bikes=data.get('bikes'),
        )
    else:
        msg = _(
            '#{pk} {emoji}\n\n'
            'Booking {action} {is_admin}{is_user} via'
            ' {via}!\n\n'
            'Booking details:\n'
            '➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
            'User: {client}\n'
            'Client\'s phone: {phone}\n'
            '📅  {date}\n'
            '🕒  {start} - {end}\n'
            '🏍 {bikes} bike(s)'
        ).format(
            pk=data.get('pk'),
            emoji=emoji.get(status),
            action=status if not status == _('pending') else _('change'),
            is_admin=_('by admin') if is_admin else _('by user'),
            is_user=client if not is_admin else '',
            via=via,
            client=data.get('client'),
            phone=data.get('phone'),
            date=data.get('date'),
            start=data.get('start'),
            end=data.get('end'),
            bikes=data.get('bikes'),
        )
    vk.send_notify(msg)
