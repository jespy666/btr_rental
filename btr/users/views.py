from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import (CreateView, DetailView, UpdateView,
                                  DeleteView)
from django.utils.translation import gettext as _

from btr.users.forms import (UserRegistrationForm, UserEditProfileImageForm,
                             UserEditForm, ChangePasswordForm)
from btr.users.models import SiteUser
from btr.mixins import (UserAuthRequiredMixin, UserPermissionMixin,
                        DeleteProtectionMixin)
from ..bookings.models import Booking
from ..tasks.users import send_hello_msg


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = SiteUser
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'forms/registration.html'
    success_message = _('User created successfully')

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get('email')
        name = form.cleaned_data.get('first_name')
        login = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password2')
        send_hello_msg.delay(email, name, login, password)
        return super().form_valid(form)


class UserView(UserAuthRequiredMixin, DetailView):
    model = SiteUser
    template_name = 'users/profile.html'
    context_object_name = 'profile'
    login_url = 'login'
    permission_denied_message = _('You must to be log in')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        completed_bookings = Booking.objects.filter(
            rider=user,
            status__in=[_('completed'), _('canceled')],
        )
        current_bookings = Booking.objects.filter(rider=user).exclude(
            status__in=[_('completed'), _('canceled')],
        )
        context['completed_bookings'] = completed_bookings
        context['current_bookings'] = current_bookings
        return context


class UserUpdateImageView(UserAuthRequiredMixin, UserPermissionMixin,
                          SuccessMessageMixin, UpdateView):
    model = SiteUser
    form_class = UserEditProfileImageForm
    template_name = 'forms/change_image.html'
    success_message = _('You are updated your profile image')
    success_url = None
    login_url = reverse_lazy('login')
    permission_denied_message = _('You must to be log in')
    permission_message = _('You can\'t change other user profile image!')
    permission_url = reverse_lazy('home')

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.request.user.id})


class UserUpdateView(UserAuthRequiredMixin, UserPermissionMixin,
                     SuccessMessageMixin, UpdateView):
    model = SiteUser
    form_class = UserEditForm
    template_name = 'forms/user_edit.html'
    success_message = _('Profile updated successfully')
    success_url = None
    login_url = reverse_lazy('login')
    permission_denied_message = _('You must to be log in')
    permission_message = _('You can\'t edit other user profile!')
    permission_url = reverse_lazy('home')

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.request.user.id})


class UserChangePasswordView(SuccessMessageMixin, PasswordChangeView):

    form_class = ChangePasswordForm
    template_name = 'forms/change_password.html'
    success_url = None
    success_message = _('Password changed successfully')

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.request.user.id})


class UserDeleteView(UserAuthRequiredMixin, UserPermissionMixin,
                     DeleteProtectionMixin, SuccessMessageMixin, DeleteView):

    model = SiteUser
    template_name = 'forms/user_delete.html'
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('home')
    success_message = _('User delete successfully')
    permission_message = _('You do not have permission to delete another user')
    permission_url = success_url
    protection_message = _('Can\'t delete user with existed bookings')
    protected_url = reverse_lazy('home')
    permission_denied_message = _('You must to be log in')
