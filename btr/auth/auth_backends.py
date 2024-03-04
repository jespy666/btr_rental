from django.contrib.auth.backends import ModelBackend

from btr.users.models import SiteUser


class MultiplyFieldBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = SiteUser.objects.get(username=username.lower())
        except SiteUser.DoesNotExist:
            try:
                user = SiteUser.objects.get(email=username.lower())
            except SiteUser.DoesNotExist:
                try:
                    user = SiteUser.objects.get(phone_number=username)
                except SiteUser.DoesNotExist:
                    return None

        if user.check_password(password):
            return user
