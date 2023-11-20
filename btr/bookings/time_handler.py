from datetime import datetime, timedelta


def calculate_time_interval(start_time, hours):
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(hours=hours)
        time_interval = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        return time_interval
    except ValueError:
        return None
