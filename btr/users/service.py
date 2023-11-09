from django.core.mail import send_mail
from django.utils.translation import gettext as _


def send(user_email):
    send_mail(
        _('Welcome'),
        _('Welcome  to BroTeamRacing!'),
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )