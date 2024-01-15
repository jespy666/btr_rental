from datetime import datetime, timedelta
import secrets
import string
#
from django.conf import settings
#
# from .bot_exceptions import BusyDayException, TimeIsNotAvailable, \
#     WrongAdminPassword
#
#


#
#

#
#
# def check_admin_password(password: str) -> bool:
#     """Compares admin password with user type"""
#     if password == settings.TG_ADMIN_PASSWORD:
#         return True
#     raise WrongAdminPassword
#
#
# def extract_start_times(time_intervals: list) -> list:
#     """Get all available start times to bot buttons"""
#     start_times = []
#     for start, end in time_intervals:
#         start_dt = datetime.strptime(start, '%H:%M')
#         end_dt = datetime.strptime(end, '%H:%M')
#         hours_difference = (end_dt - start_dt).seconds // 3600
#         start_times.extend(
#             [(start_dt + timedelta(hours=i)).strftime('%H:%M') for i in
#              range(hours_difference)])
#
#     return start_times
#
#

