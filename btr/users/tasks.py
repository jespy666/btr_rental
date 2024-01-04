from .service import send, send_from_tg, send_verification_code, \
    send_recover_message
from ..celery import app


@app.task
def send_reg_email(user_email: str) -> None:
    """Task work out when user signed up"""
    send(user_email)


@app.task
def send_data_from_tg(email: str, name: str, username: str,
                      phone_number: str, password: str) -> None:
    """Task send sign up details to email"""
    send_from_tg(email, name, username, phone_number, password)


@app.task
def send_verification_code_from_tg(email: str, code: str) -> None:
    """Task send verification code when user request password reset from tg"""
    send_verification_code(email, code)


@app.task
def send_recover_message_from_tg(email: str, password: str) -> None:
    """Task send recovered details to email via tg bot"""
    send_recover_message(email, password)
