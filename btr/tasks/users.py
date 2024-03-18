from ..celery import app
from ..emails import (verification_code_mail, recover_message_mail,
                      registration_mail)


@app.task
def send_hello_msg(**kwargs) -> None:
    """Send hello message after sign up"""
    registration_mail(
        kwargs.get('email'),
        kwargs.get('name'),
        kwargs.get('login'),
        kwargs.get('password'),
    )


@app.task
def send_verification_code(**kwargs) -> None:
    """Task work out when user request password reset"""
    verification_code_mail(kwargs.get('email'), kwargs.get('code'))


@app.task
def send_recover_message(**kwargs) -> None:
    """Task send new password to user"""
    recover_message_mail(
        kwargs.get('email'),
        kwargs.get('password'),
        kwargs.get('username'),
    )
