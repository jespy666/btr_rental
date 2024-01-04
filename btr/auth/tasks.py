from btr.users.service import send_verification_code, send_recover_message
from btr.celery import app


@app.task
def send_verification_code_from_site(email: str, code: str) -> None:
    """Task work out when user request password reset from site"""
    send_verification_code(email, code)


@app.task
def send_recover_message_from_site(email: str, password: str) -> None:
    """Task send new password to user from site"""
    send_recover_message(email, password)
