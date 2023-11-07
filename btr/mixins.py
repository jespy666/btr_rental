from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
