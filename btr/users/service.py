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


def send_from_tg(user_email, name, password):
    subject = _('Created an new account on broteamracing.ru')
    message = _(
        'Hello, {name}!\n'
        'You are received this mail, because you are signed up with telegram\n'
        'Here are your sign-in details:\n'
        'Login: {user_email} *or phone/username\n'
        'Password: {password}'
    ).format(name=name, user_email=user_email, password=password)

    send_mail(
        subject,
        message,
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )
