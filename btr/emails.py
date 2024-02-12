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
        'emails/recover.html', {
            'emails': user_email,
            'password': password
        }
    )
    text_content = _(
        'There are recovered data to sign in:\n'
        'Login: {emails}\n'
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


def registration_mail(email: str, name: str, login: str,
                      password: str) -> None:
    """Mail with hello message"""
    subject = _('Hello from BroTeamRacing')
    html_content = render_to_string(
        'emails/registration.html', {
            'first_name': name,
            'login': login,
            'password': password,
        }
    )
    text_content = _(
        'Glad to see you in our Rental:\n'
        'Login: {login}\n'
        'Password: {password}\n'
    ).format(login=login, password=password)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def create_booking_mail(email: str, name: str, date: str, status: str,
                        start: str, end: str, bikes: str, pk: str) -> None:
    """Mail with new booking details"""
    subject = _('New Booking Created')
    html_content = render_to_string(
        'emails/create_booking.html', {
            'name': name,
            'date': date,
            'start': start,
            'end': end,
            'bikes': bikes,
            'status': status,
            'id': pk,
        }
    )
    text_content = _(
        'You made booking nearly!\n'
        'Details:\n'
        'Date: {date}\n'
        'Time: {start}-{end}\n'
        'Bikes requested: {bikes}\n'
        'Current status: {status}\n'
        'We have already seen your entry, we will confirm it soon!\n'
        'You will also receive information about the change of status'
        ' by email\nSee you soon  - BTR Team'
    ).format(date=date, start=start, end=end, bikes=bikes, status=status)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def confirm_booking_mail(email: str, pk: str, bikes: str,
                         date: str, start: str, end: str) -> None:
    """Mail with confirm booking message"""
    subject = _('Booking Confirmed')
    html_content = render_to_string(
        'emails/confirm_booking.html', {
            'date': date,
            'start': start,
            'end': end,
            'bikes': bikes,
            'id': pk,
        }
    )
    text_content = _(
        'Booking #{pk} confirmed successfully!\n'
        'We are waiting for you at the appointed time!\n'
        'If you are unable to attend your rental, please cancel in advance.\n'
        'See you soon - <em>BroTeamRacing Team</em>'
    ).format(pk=pk)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def cancel_booking_mail(email: str, pk: str, date: str,
                        start: str, end: str, self_cancel=False) -> None:
    """Mail with canceled booking message"""
    subject = _('Booking Canceled')
    if not self_cancel:
        html_content = render_to_string(
            'emails/cancel_booking.html', {
                'date': date,
                'id': pk,
                'start': start,
                'end': end,
            }
        )
        text_content = _(
            'Booking #{pk} was canceled :(!\n'
            'Unfortunately, we will not be able'
            ' to see you at the scheduled time\n'
            'Please choose another time or contact us by phone.'
        ).format(pk=pk)
    else:
        html_content = render_to_string(
            'emails/cancel_booking_self.html', {
                'date': date,
                'id': pk,
                'start': start,
                'end': end,
            }
        )
        text_content = _(
            'Booking #{pk} was canceled :(!\n'
            'You are canceled booking!\n'
            'If you have questions, contact us!'
        ).format(pk=pk)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
