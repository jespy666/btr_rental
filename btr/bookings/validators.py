from datetime import datetime, timedelta


def validate_slots(available_slots: list, desired_slot: tuple) -> bool:
    """Check if time range is available"""
    desired_start, desired_end = desired_slot
    if desired_start >= desired_end:
        return False
    for start, end in available_slots:
        if desired_start >= start and desired_end <= end:
            return True
    return False


def validate_start_time(time: datetime.time, date: str) -> bool:
    """Checks start time not in past"""
    now = datetime.now()
    formatted_date = datetime.strptime(date, '%Y-%B-%d')
    full_date = datetime.combine(formatted_date.date(), time)
    return full_date > now


def validate_equal_hour(start: datetime.time, end: datetime.time) -> bool:
    """Check common time is equal to hour"""
    start_datetime = datetime.combine(datetime.today(), start)
    end_datetime = datetime.combine(datetime.today(), end)

    diff = end_datetime - start_datetime
    one_hour = timedelta(hours=1)

    return diff.total_seconds() % one_hour.total_seconds() == 0
