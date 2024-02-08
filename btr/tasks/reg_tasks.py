from ..celery import app
from ..emails import (send_tg_reg_info, send_verification_code,
                      send_recover_message, registration_mail)


@app.task
def send_hello_email(email: str, name: str, login: str, password: str) -> None:
    """Send hello message after sign up"""
    registration_mail(email, name, login, password)


@app.task
def send_reg_data_from_tg(email: str, name: str, username: str,
                          phone_number: str, password: str) -> None:
    """Task send sign up details to emails"""
    send_tg_reg_info(email, name, username, phone_number, password)


@app.task
def send_verification_code_from_tg(email: str, code: str) -> None:
    """Task send verification code when user request password reset from tg"""
    send_verification_code(email, code)


@app.task
def send_recover_message_from_tg(email: str, password: str) -> None:
    """Task send recovered details to emails via tg bot"""
    send_recover_message(email, password)


@app.task
def send_verification_code_from_site(email: str, code: str) -> None:
    """Task work out when user request password reset from site"""
    send_verification_code(email, code)


@app.task
def send_recover_message_from_site(email: str, password: str) -> None:
    """Task send new password to user from site"""
    send_recover_message(email, password)
