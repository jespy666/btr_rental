from datetime import datetime, timedelta


def calculate_time_interval(start_time: str, hours: int):
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(hours=hours)
        time_interval = {
            'start_time': start.strftime('%H:%M'),
            'end_time': end.strftime('%H:%M'),
        }
        return time_interval
    except ValueError:
        return None
