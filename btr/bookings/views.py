from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, \
    TemplateView
from django.utils.translation import gettext as _
import datetime
import calendar

from btr.mixins import UserAuthRequiredMixin, UserPermissionMixin
from .models import Booking
from .forms import BookingForm


class BookingIndexView(TemplateView):
    template_name = 'bookings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        current_cal = calendar.monthcalendar(current_year, current_month)
        context['calendar'] = current_cal
        context['current_month'] = calendar.month_name[current_month]
        context['current_year'] = current_year
        return context


class BookingCreateView(UserAuthRequiredMixin, SuccessMessageMixin,
                        CreateView):

    model = Booking
    form_class = BookingForm
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')
    template_name = 'bookings/form.html'
    success_message = _('Reservation created successfully')
    permission_denied_message = _('You must to be login to book ride')
    extra_context = {
        'header': _('Rental Reservation'),
        'button': _('Book')
    }


class BookingEditView(UserAuthRequiredMixin, UserPermissionMixin,
                      SuccessMessageMixin, UpdateView):

    model = Booking
    form_class = BookingForm
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')
    template_name = 'bookings/form.html'
    success_message = _('Reservation change successfully')
    permission_denied_message = _('You must to be login to edit bookings')
    permission_message = _('You can\'t change another user bookings!')
    permission_url = success_url
    extra_context = {
        'header': _('Edit Reservation'),
        'button': _('Apply'),
    }


class BookingDeleteView(UserAuthRequiredMixin, UserPermissionMixin,
                        SuccessMessageMixin, DeleteView):

    model = Booking
    template_name = 'bookings/delete.html'
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('home')
    success_message = _('Booking delete successfully')
    permission_message = _(
        'You do not have permission to delete booking of another user!'
    )
    permission_url = success_url
    permission_denied_message = _('You must to be log in')
