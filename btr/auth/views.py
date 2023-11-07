from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext as _


class AuthLoginView(SuccessMessageMixin, LoginView):
    template_name = 'auth_form.html'
    next_page = reverse_lazy('home')
    success_message = _('You are log in')
    extra_context = {
        'header': 'Sign In',
        'button': 'Entry',
    }


class AuthLogoutView(SuccessMessageMixin, LogoutView):
    next_page = reverse_lazy('home')
    success_message = _('You are logout')

    def dispatch(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super().dispatch(request, *args, **kwargs)
