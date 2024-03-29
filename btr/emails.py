from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def verification_code_mail(email: str, code: str) -> None:
    """
    Send an email with a verification code for password reset.

    Args:
        email (str): The recipient email address.
        code (str): The verification code to include in the email.

    Returns:
        None
    """
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
    """
    Send an email with recovered sign-in data.

    Args:
        email (str): The recipient email address.
        password (str): The recovered password to include in the email.
        username (str): The recovered username to include in the email.

    Returns:
        None
    """
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
    """
    Send an email with a welcome message after sign up.

    Args:
        email (str): The recipient email address.
        name (str): The name of the user.
        login (str): The username of the user.
        password (str): The password of the user.

    Returns:
        None
    """
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
    """
    Send an email with details of a new booking.

    Args:
        email (str): The recipient email address.
        name (str): The name of the user.
        date (str): The date of the booking.
        status (str): The status of the booking.
        start (str): The start time of the booking.
        end (str): The end time of the booking.
        bikes (str): The number of bikes for the booking.
        pk (str): The primary key of the booking.

    Returns:
        None
    """
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
    """
    Email confirm a booking.

    Args:
        email (str): The recipient email address.
        pk (str): The primary key of the booking.
        bikes (str): The number of bikes for the booking.
        date (str): The date of the booking.
        start (str): The start time of the booking.
        end (str): The end time of the booking.

    Returns:
        None
    """
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
    """
    Send an email with a canceled booking message.

    Args:
        email (str): The recipient email address.
        pk (str): The primary key of the booking.
        bikes (str): The number of bikes for the booking.
        date (str): The date of the booking.
        start (str): The start time of the booking.
        end (str): The end time of the booking.
        self_cancel (bool, optional): A flag indicating whether the booking
         was canceled by the user themselves. Defaults to False.

    Returns:
        None
    """
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


def edit_booking_mail(email: str, pk: str, bikes: str, date: str, start: str,
                      end: str, self_edit=False) -> None:
    """
    Send an email with a booking edited message.

    Args:
        email (str): The recipient email address.
        pk (str): The primary key of the booking.
        bikes (str): The number of bikes for the booking.
        date (str): The date of the booking.
        start (str): The start time of the booking.
        end (str): The end time of the booking.
        self_edit (bool, optional): A flag indicating whether the booking was
         edited by the user themselves. Defaults to False.

    Returns:
        None
    """
    subject = _('Booking edited')
    if not self_edit:
        html_content = render_to_string(
            'emails/email_base.html', {
                'pre_header': _('Booking was edited'),
                'header': _('Booking Edited'),
                'action': 'edit',
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
                'pre_header': _('You are edit the booking'),
                'header': _('Booking Edited'),
                'action': 'self-edit',
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
