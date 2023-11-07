from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext as _

from .models import SiteUser, UserProfile
from .forms import UserRegistrationForm
from ..mixins import UserAuthRequiredMixin, UserPermissionMixin


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = SiteUser
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'auth_form.html'
    success_message = _('User created successfully')
    extra_context = {
        'header': _('Registration'),
        'button': _('Sign Up'),
    }


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = 'auth_form.html'
    next_page = reverse_lazy('home')
    success_message = _('You are log in')
    extra_context = {
        'header': 'Sign In',
        'button': 'Entry',
    }


class UserLogoutView(SuccessMessageMixin, LogoutView):
    next_page = reverse_lazy('home')
    success_message = _('You are logout')

    def dispatch(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(UserAuthRequiredMixin, DetailView):
    model = SiteUser
    template_name = 'users/profile.html'

    context_object_name = 'profile'

    login_url = 'login'
    permission_denied_message = _('You must to be log in')


