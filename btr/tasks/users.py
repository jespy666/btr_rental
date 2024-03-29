from ..celery import app
from ..emails import (verification_code_mail, recover_message_mail,
                      registration_mail)


@app.task
def send_hello_msg(**kwargs) -> None:
    """
    Send a hello message after sign-up.

    Args:
        **kwargs: Keyword arguments containing user details.

    Example:
        send_hello_msg(
            email='user@example.com',
            name='John Doe',
            login='john_doe',
            password='secret123'
        )
    """
    registration_mail(
        kwargs.get('email'),
        kwargs.get('name'),
        kwargs.get('login'),
        kwargs.get('password'),
    )


@app.task
def send_verification_code(**kwargs) -> None:
    """
    Send a verification code for password reset.

    Args:
        **kwargs: Keyword arguments containing user details.

    Example:
        send_verification_code(email='user@example.com', code='123456')
    """
    verification_code_mail(kwargs.get('email'), kwargs.get('code'))


@app.task
def send_recover_message(**kwargs) -> None:
    """
    Task to send a new password to the user.

    Args:
        **kwargs: Keyword arguments containing the following:
            - email (str): User's email address.
            - password (str): New password to be sent.
            - username (str): User's username.

    Returns:
        None
    """
    recover_message_mail(
        kwargs.get('email'),
        kwargs.get('password'),
        kwargs.get('username'),
    )
