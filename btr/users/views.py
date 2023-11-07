from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.utils.translation import gettext as _

from btr.users.forms import UserRegistrationForm, UserEditForm
from btr.users.models import SiteUser
from btr.mixins import UserAuthRequiredMixin, UserPermissionMixin


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


class UserView(UserAuthRequiredMixin, DetailView):
    model = SiteUser
    template_name = 'users/profile.html'

    context_object_name = 'profile'

    login_url = 'login'
    permission_denied_message = _('You must to be log in')


class UserUpdateView(UserAuthRequiredMixin, UserPermissionMixin,
                     SuccessMessageMixin, UpdateView):

    model = SiteUser
    form_class = UserEditForm
    template_name = 'users/edit.html'
    success_message = _('Profile successfully updated')
    success_url = reverse_lazy('home')


