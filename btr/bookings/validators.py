from datetime import datetime, timedelta


def validate_slots(available_slots: list, desired_slot: tuple) -> bool:
    """
    Check if the desired time slot is available.

    Args:
        available_slots (list): List of available time slots.
        desired_slot (tuple): Tuple containing desired start and end times.

    Returns:
        bool: True if the slot is available, False otherwise.
    """
    desired_start, desired_end = desired_slot
    if desired_start >= desired_end:
        return False
    for start, end in available_slots:
        if desired_start >= start and desired_end <= end:
            return True
    return False


def validate_start_time(time: datetime.time, date: str) -> bool:
    """
    Check if the start time is not in the past.

    Args:
        time (datetime.time): The desired start time.
        date (str): The current date in the format '%Y-%m-%d'.

    Returns:
        bool: True if the start time is valid, False otherwise.

    Example:
        validate_start_time(desired_start_time, '2024-03-29')
    """
    now = datetime.now()
    formatted_date = datetime.strptime(date, '%Y-%m-%d')
    full_date = datetime.combine(formatted_date.date(), time)
    return full_date > now


def validate_equal_hour(start: datetime.time, end: datetime.time) -> bool:
    """
    Check if the common ride time is equal to an hour.

    Args:
        start (datetime.time): The start time.
        end (datetime.time): The end time.

    Returns:
        bool: True if the duration is equal to an hour, False otherwise.

    Example:
        validate_equal_hour(start_time, end_time)
    """
    start_datetime = datetime.combine(datetime.today(), start)
    end_datetime = datetime.combine(datetime.today(), end)

    diff = end_datetime - start_datetime
    one_hour = timedelta(hours=1)

    return diff.total_seconds() % one_hour.total_seconds() == 0


def validate_bikes(bikes: str) -> bool:
    """
    Validate the number of bikes requested.

    Args:
        bikes (str): The number of bikes requested.

    Returns:
        bool: True if the bike count is valid, False otherwise.

    Example:
        validate_bikes('3')
    """
    return 1 <= int(bikes) <= 4
