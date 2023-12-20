from datetime import datetime, timedelta
import secrets
import string


def calculate_time_interval(start_time: str, hours: str) -> dict | None:
    """Calculate end time by hours"""
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(hours=int(hours))
        time_interval = {
            'start_time': start.strftime('%H:%M'),
            'end_time': end.strftime('%H:%M'),
        }
        return time_interval
    except ValueError:
        return None


def generate_verification_code() -> str:
    """Generate random code to confirm personality"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))


def check_verification_code(source_code: str, user_code: str) -> bool:
    """Check that the verification codes match"""
    if source_code == user_code:
        return True
    else:
        raise ValueError
