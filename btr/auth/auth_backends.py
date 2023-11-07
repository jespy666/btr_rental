from django.contrib.auth.backends import ModelBackend

from .models import SiteUser


class EmailOrNumberBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = SiteUser.objects.get(username=username)
        except SiteUser.DoesNotExist:
            try:
                user = SiteUser.objects.get(email=username)
            except SiteUser.DoesNotExist:
                try:
                    user = SiteUser.objects.get(phone_number=username)
                except SiteUser.DoesNotExist:
                    return None

        if user.check_password(password):
            return user
