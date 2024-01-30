from datetime import datetime
import calendar

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, UpdateView, DeleteView,
                                  TemplateView)
from django.utils.translation import gettext as _

from ..mixins import UserAuthRequiredMixin, UserPermissionMixin
from .models import Booking
from .forms import BookingForm
from .locale import locale_month_name
from ..orm_utils import LoadCalc
from ..tasks.book_tasks import send_details


class BookingIndexView(TemplateView):
    template_name = 'bookings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        current_cal = calendar.monthcalendar(current_year, current_month)
        if current_month == 12:
            next_year = current_year + 1
            next_month = 1
        else:
            next_year = current_year
            next_month = current_month + 1
        current_load = LoadCalc(current_cal, current_year,
                                current_month).get_month_load()
        next_cal = calendar.monthcalendar(next_year, next_month)
        next_load = LoadCalc(next_cal, next_year, next_month).get_month_load()
        context['current_month'] = calendar.month_name[current_month]
        context['verbose_month'] = locale_month_name(
            calendar.month_name[current_month]
        )
        context['current_year'] = current_year
        context['today'] = current_day
        context['current_calendar'] = current_load
        context['next_month'] = calendar.month_name[next_month]
        context['verbose_next_month'] = locale_month_name(
            calendar.month_name[next_month]
        )
        context['next_year'] = next_year
        context['next_calendar'] = next_load
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
        'header': _('Rental Reservation for'),
        'button': _('Book')
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['available_slots'] = self.request.GET.get('slots')
        kwargs['current_date'] = self.request.GET.get('selected_date')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_date = self.request.GET.get('selected_date')
        verbose_month = self.request.GET.get('verbose_month')
        verbose_current_month = verbose_month if verbose_month else (
            self.request.GET.get('verbose_next_month'))
        slots = self.request.GET.get('slots')
        formatted_date = self.format_date_for_form(selected_date)
        context['selected_date'] = formatted_date
        context['ranges'] = eval(slots)
        context['verbose_month'] = verbose_current_month
        return context

    @staticmethod
    def format_date_for_form(date: str) -> str:
        """Friendly view date format"""
        date_elements = date.split('-')
        return f'{date_elements[2]} {date_elements[1]}, {date_elements[0]}'

    @staticmethod
    def format_date_for_orm(date: str) -> str:
        """Format month name to number"""
        date_object = datetime.strptime(date, '%Y-%B-%d')
        formatted_date = date_object.strftime('%Y-%m-%d')
        return formatted_date

    def form_valid(self, form):
        selected_date = self.request.GET.get('selected_date')
        start_time = form.cleaned_data.get('start_time')
        end_time = form.cleaned_data.get('end_time')
        bike_count = form.cleaned_data.get('bike_count')
        user = self.request.user
        user_email = user.email
        form.instance.booking_date = self.format_date_for_orm(selected_date)
        form.instance.rider = user
        if user.is_superuser:
            form.instance.status = _('confirmed')
        else:
            form.instance.status = _('pending')
        form.save()
        send_details.delay(user_email, selected_date,
                           start_time, end_time, bike_count)
        return super().form_valid(form)


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
