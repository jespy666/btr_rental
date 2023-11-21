from django.core.mail import send_mail
from django.utils.translation import gettext as _


def send_booking_details(user_email, date, start_time, end_time):
    subject = _('A new booking create')
    message = _(
        'Hi, Rider!\n'
        'We get a info about booking your made nearly!\n'
        'Here\'s details:\n'
        'Date: {date}\n'
        'Time: from {start} to {end}\n'
        'If you are late or cancel your race, please notify us in advance!\n'
        'Contact number: +7 999 235-00-91\n'
        'See you soon!'
    ).format(date=date, start=start_time, end=end_time)
    send_mail(
        subject,
        message,
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )
