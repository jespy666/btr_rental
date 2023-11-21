from btr.bookings.service import send_booking_details
from btr.celery import app


@app.task
def send_details(user_email, date, start, end):
    send_booking_details(user_email, date, start, end)
