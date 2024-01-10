from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def send_tg_reg_info(user_email, name, username, phone_number, password):
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
    html_content = render_to_string(
        'email/recover.html', {
            'email': user_email,
            'password': password
        }
    )
    text_content = _(
        'There are recovered data to sign in:\n'
        'Login: {email}\n'
        'Password: {password}\n'
    ).format(email=user_email, password=password)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        'broteamracing@yandex.ru',
        [user_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_booking_details(user_email, date, start_time, end_time, bike_count):
    subject = _('A new booking create')
    message = _(
        'Hi, Rider!\n'
        'We get a info about booking your made nearly!\n'
        'Here\'s details:\n'
        'Date: {date}\n'
        'Time: from {start} to {end}\n'
        'Number of bikes: {bike_count}\n'
        'If you are late or cancel your race, please notify us in advance!\n'
        'Contact number: +7 999 235-00-91\n'
        'See you soon!'
    ).format(date=date, start=start_time, end=end_time, bike_count=bike_count)
    send_mail(
        subject,
        message,
        'broteamracing@yandex.ru',
        [user_email],
        fail_silently=False,
    )
