from .service import send
from ..celery import app


@app.task
def send_reg_email(user_email):
    send(user_email)
