from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import gettext as _

from btr.users.forms import UserRegistrationForm, UserEditForm
from btr.users.models import SiteUser
from btr.mixins import UserAuthRequiredMixin, UserPermissionMixin, \
    DeleteProtectionMixin
from ..bookings.models import Booking


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = SiteUser
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'forms/registration.html'
    success_message = _('User created successfully')

    def form_valid(self, form):
        form.save()
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


class UserUpdateView(UserAuthRequiredMixin, UserPermissionMixin,
                     SuccessMessageMixin, UpdateView):

    model = SiteUser
    form_class = UserEditForm
    template_name = 'forms/user_edit.html'
    success_message = _('Profile successfully updated')
    success_url = reverse_lazy('login')
    login_url = success_url
    permission_denied_message = _('You must to be log in')
    permission_message = _('You can\'t edit another profile!')
    permission_url = reverse_lazy('home')


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
