from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext as _
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist

from btr.auth.forms import AuthPasswordResetForm, AuthConfirmForm
from ..tasks.users import send_verification_code, send_recover_message
from btr.tg_bot.utils.handlers import generate_verification_code
from ..mixins import ObjectDoesNotExistMixin
from btr.users.models import SiteUser


class AuthLoginView(SuccessMessageMixin, LoginView):
    template_name = 'forms/auth.html'
    next_page = reverse_lazy('home')
    success_message = _('You are log in')


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
    template_name = 'forms/password_reset.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email').lower()
        form.cleaned_data['email'] = email
        SiteUser.objects.get(email=email)
        # generate secret code
        code = generate_verification_code()
        # send secret code on user email
        send_verification_code.delay(email=email, code=code)
        # keep secret code in session
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
    template_name = 'forms/confirm_code.html'

    def form_valid(self, form):
        # get secret code from session
        verification_code = self.request.session.get('verification_code')
        email = self.request.session.get('user_email')
        user_code = form.cleaned_data.get('code')
        try:
            if verification_code == user_code:
                password = SiteUser.objects.make_random_password(length=8)
                user = SiteUser.objects.get(email=email)
                user.set_password(password)
                user.save()
                # send recover message to user email with new sign in data
                send_recover_message.delay(
                    email=email,
                    password=password,
                    username=user.username,
                )
                return super().form_valid(form)
            else:
                messages.error(
                    self.request,
                    _('Verification codes not match')
                )
                return self.form_invalid(form)
        except ObjectDoesNotExist:
            messages.error(
                self.request,
                _('User with this email does not exist!')
            )
            return self.form_invalid(form)
