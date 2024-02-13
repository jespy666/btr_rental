from ..celery import app
from ..emails import (verification_code_mail, recover_message_mail,
                      registration_mail)


@app.task
def send_hello_msg(email: str, name: str, login: str, password: str) -> None:
    """Send hello message after sign up"""
    registration_mail(email, name, login, password)


@app.task
def send_verification_code(email: str, code: str) -> None:
    """Task work out when user request password reset from site"""
    verification_code_mail(email, code)


@app.task
def send_recover_message(email: str, password: str, username: str) -> None:
    """Task send new password to user from site"""
    recover_message_mail(email, password, username)
