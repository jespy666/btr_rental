from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def verification_code_mail(email: str, code: str) -> None:
    """Mail with verification code"""
    subject = _('Password reset')
    html_content = render_to_string(
        'emails/email_base.html', {
            'action': 'password-reset',
            'pre_header': _('Verification code for password reset'),
            'header': _('Password reset'),
            'code': code,
        }
    )
    msg = EmailMessage(
        subject,
        html_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()


def recover_message_mail(email: str, password: str, username: str) -> None:
    """Mail with recovered data to sign-in"""
    subject = _('Recovered Sign-In message')
    html_content = render_to_string(
        'emails/email_base.html', {
            'action': 'recover-data',
            'pre_header': _('Mail with recovered sign-in data'),
            'header': _('Recovered Sign-In Info'),
            'username': username,
            'password': password
        }
    )
    msg = EmailMessage(
        subject,
        html_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()


def registration_mail(email: str, name: str, login: str,
                      password: str) -> None:
    """Mail with hello message after sign up"""
    subject = _('Hello from BroTeamRacing')
    html_content = render_to_string(
        'emails/email_base.html', {
            'header': _('Welcome'),
            'name': name,
            'username': login,
            'password': password,
            'action': 'registration',
        }
    )
    msg = EmailMessage(
        subject,
        html_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()


def create_booking_mail(email: str, name: str, date: str, status: str,
                        start: str, end: str, bikes: str, pk: str) -> None:
    """Mail with new booking details"""
    subject = _('New Booking Created')
    html_content = render_to_string(
        'emails/email_base.html', {
            'pre_header': _('An new booking created nearly'),
            'header': _('New Booking Created'),
            'action': 'create',
            'name': name,
            'date': date,
            'start': start,
            'end': end,
            'bikes': bikes,
            'status': status,
            'pk': pk,
        }
    )
    msg = EmailMessage(
        subject,
        html_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()


def confirm_booking_mail(email: str, pk: str, bikes: str,
                         date: str, start: str, end: str) -> None:
    """Mail with confirm booking message"""
    subject = _('Booking Confirmed')
    html_content = render_to_string(
        'emails/email_base.html', {
            'pre_header': _('Booking confirmed successfully'),
            'header': _('Booking Confirmed'),
            'action': 'confirm',
            'date': date,
            'start': start,
            'end': end,
            'bikes': bikes,
            'pk': pk,
        }
    )
    msg = EmailMessage(
        subject,
        html_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()


def cancel_booking_mail(email: str, pk: str, bikes: str, date: str,
                        start: str, end: str, self_cancel=False) -> None:
    """Mail with canceled booking message"""
    subject = _('Booking Canceled')
    if not self_cancel:
        html_content = render_to_string(
            'emails/email_base.html', {
                'pre_header': _('Booking was canceled'),
                'header': _('Booking Canceled'),
                'action': 'cancel',
                'date': date,
                'pk': pk,
                'start': start,
                'end': end,
                'bikes': bikes,
            }
        )
    else:
        html_content = render_to_string(
            'emails/email_base.html', {
                'pre_header': _('You are canceled booking'),
                'header': _('Booking Canceled'),
                'action': 'self-cancel',
                'date': date,
                'pk': pk,
                'start': start,
                'end': end,
                'bikes': bikes,
            }
        )
    msg = EmailMessage(
        subject,
        html_content,
        'broteamracing@yandex.ru',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()
