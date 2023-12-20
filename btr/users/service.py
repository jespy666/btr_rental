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


def send_from_tg(user_email, name, username, phone_number, password):
    subject = _('Created an new account on broteamracing.ru')
    message = _(
        'Hello, {name}!\n'
        'You are received this mail, because you are signed up with telegram\n'
        'Here are your sign-in details:\n'
        'Email: {user_email}\n'
        'Username: {username}\n'
        'Phone number: {phone_number}\n'
        '*to enter the site you can use any of the three fields'
        'Password: {password}'
    ).format(
        name=name,
        user_email=user_email,
        username=username,
        phone_number=phone_number,
        password=password,
    )
    send_mail(
        subject,
        message,
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )


def send_verification_code(user_email, code):
    subject = _('Verification code for password reset')
    message = _(
        'Hi! You are received this message, because a password'
        ' reset was requested for your account on broteamracing.ru.\n'
        'If it wasn\'t you, ignore this message.\n'
        'YOUR VERIFICATION CODE: {code}'
    ).format(code=code)
    send_mail(
        subject,
        message,
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )


def send_recover_message(user_email, password):
    subject = _('Recovered Sign in message')
    message = _(
        'There are recovered data to sign in:\n'
        'Login: {email}\n'
        'Password: {password}\n'
    ).format(email=user_email, password=password)
    send_mail(
        subject,
        message,
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )
