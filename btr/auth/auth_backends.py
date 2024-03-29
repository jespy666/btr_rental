from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from btr.users.models import SiteUser


class MultiplyFieldBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Custom authentication backend that allows authentication using
         multiple fields (username, email, or phone number).

        Args:
            request: The HTTP request object.
            username (str): The username provided during authentication.
            password (str): The password provided during authentication.
            **kwargs: Additional keyword arguments.

        Returns:
            SiteUser or None: Returns the authenticated user if valid
             credentials are provided, otherwise returns None.
        """
        try:
            user = SiteUser.objects.get(username=username)
        except ObjectDoesNotExist:
            try:
                # must be any register for email field
                user = SiteUser.objects.get(email=username.lower())
            except ObjectDoesNotExist:
                try:
                    user = SiteUser.objects.get(phone_number=username)
                except ObjectDoesNotExist:
                    return None

        if user.check_password(password):
            return user
