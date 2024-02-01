from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext as _
from django.views.generic import FormView

from btr.auth.forms import AuthPasswordResetForm, AuthConfirmForm
from ..orm_utils import reset_user_password, check_user_exist
from ..tasks.reg_tasks import (send_verification_code_from_site,
                               send_recover_message_from_site)
from btr.tg_bot.utils.handlers import generate_verification_code
from ..mixins import ObjectDoesNotExistMixin


class AuthLoginView(SuccessMessageMixin, LoginView):
    template_name = 'modals/guest.html'
    next_page = reverse_lazy('home')
    success_message = _('You are log in')
    extra_context = {
        'header': _('Sign In'),
        'button': _('Entry'),
    }


class AuthLogoutView(SuccessMessageMixin, LogoutView):
    next_page = reverse_lazy('home')
    success_message = _('You are logout')

    def dispatch(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super().dispatch(request, *args, **kwargs)


class AuthResetView(SuccessMessageMixin, ObjectDoesNotExistMixin, FormView):
    form_class = AuthPasswordResetForm
    success_url = reverse_lazy('confirm')
    success_message = _('Verification code was send to your email')
    not_existed_message = _('User with this email does not exist')
    not_existed_url = reverse_lazy('auth-reset')
    template_name = 'password_reset_form.html'
    extra_context = {
        'header': _('Password reset'),
        'button': _('Send'),
    }

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        check_user_exist(email)
        code = generate_verification_code()
        send_verification_code_from_site.delay(email, code)
        self.request.session['verification_code'] = code
        self.request.session['user_email'] = email
        return super().form_valid(form)


class ConfirmCodeView(SuccessMessageMixin, FormView):
    form_class = AuthConfirmForm
    success_url = reverse_lazy('login')
    success_message = _(
        'Your password was successfully reset!\n'
        'New password was send on your email'
    )
    template_name = 'confirm_code_form.html'
    extra_context = {
        'header': _('Verification code confirm'),
        'button': _('Confirm'),
    }

    def form_valid(self, form):
        verification_code = self.request.session.get('verification_code')
        email = self.request.session.get('user_email')
        user_code = form.cleaned_data.get('code')
        if verification_code == user_code:
            password = reset_user_password(email)
            send_recover_message_from_site.delay(email, password)
            return super().form_valid(form)
        else:
            messages.error(
                self.request,
                _('Verification codes not match'))
            return self.form_invalid(form)
