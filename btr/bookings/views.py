from datetime import datetime, date
import calendar
import ast

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import (CreateView, UpdateView, TemplateView,
                                  DetailView)
from django.utils.translation import gettext as _

from ..mixins import UserAuthRequiredMixin, BookingPermissionMixin
from .models import Booking
from .forms import BookingForm, BookingEditForm, BookingCancelForm
from ..orm_utils import LoadCalc, SlotsFinder, AsyncTools
from ..tasks.admin import send_vk_notify
from ..tasks.bookings import (send_booking_details, send_cancel_self_message,
                              send_self_edit_booking_message)


class BookingIndexView(TemplateView):

    template_name = 'bookings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        # get data for current month
        current_cal = calendar.monthcalendar(current_year, current_month)
        # check if not last month in year
        if current_month == 12:
            next_year = current_year + 1
            next_month = 1
        else:
            next_year = current_year
            next_month = current_month + 1
        # get load in percentage on current month
        current_load = LoadCalc(current_cal, current_year, current_month)
        next_cal = calendar.monthcalendar(next_year, next_month)
        next_load = LoadCalc(next_cal, next_year, next_month)
        update_context = {
            'current_month': date(current_year, current_month, 1),
            'current_year': current_year,
            'current_calendar': current_load.get_month_load(),
            'today': current_day,
            'next_month': date(next_year, next_month, 1),
            'next_year': next_year,
            'next_calendar': next_load.get_month_load(),
        }
        context.update(update_context)
        return context


class BookingDetailView(UserAuthRequiredMixin, BookingPermissionMixin,
                        DetailView):

    template_name = 'bookings/show.html'
    model = Booking
    login_url = reverse_lazy('login')
    permission_denied_message = _('You must to be login')
    foreign_book_message = _('You cannot see another user bookings')
    foreign_book_url = reverse_lazy('home')


class BookingCreateView(UserAuthRequiredMixin, SuccessMessageMixin,
                        CreateView):

    model = Booking
    form_class = BookingForm
    success_url = None
    login_url = reverse_lazy('login')
    template_name = 'forms/booking_create.html'
    success_message = _('Reservation created successfully')
    permission_denied_message = _('You must to be login to book ride')

    def get_form_kwargs(self):
        """
        Provide chosen date and time slots to form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['available_slots'] = self.request.GET.get('slots')
        kwargs['current_date'] = self.request.GET.get('selected_date')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_date = self.request.GET.get('selected_date')
        slots: str = self.request.GET.get('slots')
        try:
            parsed_slots = ast.literal_eval(slots)
        except (ValueError, SyntaxError):
            parsed_slots = []
        update_context = {
            'ranges': parsed_slots,
            'date': datetime.strptime(selected_date, '%Y-%m-%d').date()
        }
        context.update(update_context)
        return context

    def form_valid(self, form):
        selected_date = self.request.GET.get('selected_date')
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        friendly_date = datetime.strftime(date_obj, '%Y-%B-%d')
        user = self.request.user
        form.instance.booking_date = selected_date
        form.instance.rider = user
        # automatically set status as confirmed if executor are admin
        if user.is_superuser:
            status = _('confirmed')
            form.instance.status = status
            form.save()
        # otherwise, status are pending
        else:
            status = _('pending')
            form.instance.status = status
            instance = form.save()
            data = {
                'pk': instance.pk,
                'client': instance.rider.username,
                'email': user.email,
                'name': user.first_name,
                'date': AsyncTools().get_friendly_date(friendly_date),
                'start': form.cleaned_data.get('start_time').strftime('%H:%M'),
                'end': form.cleaned_data.get('end_time').strftime('%H:%M'),
                'bikes': form.cleaned_data.get('bike_count'),
                'phone': str(instance.rider.phone_number),
                'status': status,
            }
            via = _('Web Site')
            send_vk_notify.delay(via, True, data, is_admin=False)
            send_booking_details.delay(**data)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.request.user.id})


class BookingEditView(UserAuthRequiredMixin, BookingPermissionMixin,
                      SuccessMessageMixin, UpdateView):

    model = Booking
    form_class = BookingEditForm
    success_url = None
    login_url = reverse_lazy('login')
    template_name = 'forms/book_edit.html'
    success_message = _('Reservation change successfully')
    permission_denied_message = _('You must to be login to edit bookings')
    foreign_book_message = _('You can\'t change another user bookings!')
    foreign_book_url = success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = Booking.objects.get(pk=self.kwargs['pk'])
        slots = SlotsFinder(booking.booking_date.strftime('%Y-%m-%d'))
        excluded_slot = (booking.start_time, booking.end_time)
        context['slots'] = slots.find_available_slots(excluded_slot)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        booking = Booking.objects.get(pk=self.kwargs['pk'])
        booking_date = booking.booking_date.strftime('%Y-%m-%d')
        slots = SlotsFinder(booking_date)
        excluded_slot = (booking.start_time, booking.end_time)
        kwargs['slots'] = slots.find_available_slots(excluded_slot)
        kwargs['date'] = booking_date
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        if not user.is_superuser:
            date_obj = form.instance.booking_date.strftime('%Y-%B-%d')
            via = _('Web Site')
            data = {
                'pk': form.instance.pk,
                'client': form.instance.rider.username,
                'email': user.email,
                'name': user.first_name,
                'date': AsyncTools().get_friendly_date(date_obj),
                'start': form.cleaned_data.get('start_time').strftime('%H:%M'),
                'end': form.cleaned_data.get('end_time').strftime('%H:%M'),
                'bikes': form.cleaned_data.get('bike_count'),
                'phone': str(user.phone_number),
                'status': _('pending'),
            }
            send_vk_notify.delay(via, False, data, False)
            send_self_edit_booking_message(**data)
            form.instance.status = _('pending')
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.request.user.id})


class BookingCancelView(UserAuthRequiredMixin, SuccessMessageMixin,
                        UpdateView):
    model = Booking
    form_class = BookingCancelForm
    template_name = 'forms/book_cancel.html'
    login_url = reverse_lazy('login')
    success_url = None
    success_message = _('You are canceled the ride')
    permission_denied_message = _('You must to be Log In')

    def form_valid(self, form):
        form.save()
        booking = Booking.objects.get(pk=self.kwargs['pk'])
        booking.status = _('canceled')
        booking.save()
        booking_date = booking.booking_date.strftime('%Y-%B-%d')
        if not self.request.user.is_superuser:
            via = _('Web Site')
            data = {
                'pk': booking.pk,
                'client': booking.rider.username,
                'email': booking.rider.email,
                'date': AsyncTools().get_friendly_date(booking_date),
                'start': booking.start_time.strftime('%H:%M'),
                'end': booking.end_time.strftime('%H:%M'),
                'bikes': booking.bike_count,
                'phone': str(booking.rider.phone_number),
                'status': booking.status,
            }
            send_vk_notify.delay(via, False, data, is_admin=False)
            send_cancel_self_message.delay(**data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.request.user.id})
