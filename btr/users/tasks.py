from .service import send, send_from_tg
from ..celery import app


@app.task
def send_reg_email(user_email):
    send(user_email)


@app.task
def send_data_from_tg(user_email, name, password):
    send_from_tg(user_email, name, password)
