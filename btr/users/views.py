from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import gettext as _

from btr.users.forms import UserRegistrationForm, UserEditForm
from btr.users.models import SiteUser
from btr.mixins import UserAuthRequiredMixin, UserPermissionMixin
from .tasks import send_reg_email


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

    def form_valid(self, form):
        form.save()
        send_reg_email.delay(form.instance.email)
        return super().form_valid(form)


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
    template_name = 'users/form.html'
    success_message = _('Profile successfully updated')
    success_url = reverse_lazy('login')
    login_url = success_url
    permission_denied_message = _('You must to be log in')
    permission_message = _('You can\'t edit another profile!')
    permission_url = reverse_lazy('home')
    extra_context = {
        'header': _('Profile Edit'),
        'button': _('Save'),
    }


class UserDeleteView(UserAuthRequiredMixin, UserPermissionMixin,
                     SuccessMessageMixin, DeleteView):

    model = SiteUser
    template_name = 'users/delete.html'
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('home')
    success_message = _('User delete successfully')
    permission_message = _('You do not have permission to delete another user')
    permission_url = success_url
    permission_denied_message = _('You must to be log in')
