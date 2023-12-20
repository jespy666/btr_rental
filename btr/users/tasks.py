from .service import send, send_from_tg, send_verification_code, \
    send_recover_message
from ..celery import app


@app.task
def send_reg_email(user_email):
    send(user_email)


@app.task
def send_data_from_tg(user_email, name, username, phone_number, password):
    send_from_tg(user_email, name, username, phone_number, password)


@app.task
def send_verification_code_from_tg(user_email, code):
    send_verification_code(user_email, code)


@app.task
def send_recover_message_from_tg(user_email, password):
    send_recover_message(user_email, password)
