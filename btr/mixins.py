from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.shortcuts import redirect


class UserAuthRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class UserPermissionMixin(UserPassesTestMixin):

    permission_message = None
    permission_url = None

    def test_func(self):
        return self.get_object() == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, self.permission_message)
        return redirect(self.permission_url)


class ObjectDoesNotExistMixin:

    not_existed_message = None
    not_existed_url = None

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.error(request, self.not_existed_message)
            return redirect(self.not_existed_url)


class DeleteProtectionMixin:

    protection_message = None
    protected_url = None

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, self.protection_message)
            return redirect(self.protected_url)
