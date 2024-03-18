from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from btr.users.models import SiteUser


class MultiplyFieldBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = SiteUser.objects.get(username=username)
        except ObjectDoesNotExist:
            try:
                user = SiteUser.objects.get(email=username.lower())
            except ObjectDoesNotExist:
                try:
                    user = SiteUser.objects.get(phone_number=username)
                except ObjectDoesNotExist:
                    return None

        if user.check_password(password):
            return user
