from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Booking
from .validators import (validate_slots, validate_start_time,
                         validate_equal_hour, validate_bikes)


class BookingForm(forms.ModelForm):
    """
    Custom form for booking management.

    Usage:
        Form automatically get available slots and set chosen date from view.
    """
    def __init__(self, *args, **kwargs):
        available_slots = kwargs.pop('available_slots', None)
        current_date = kwargs.pop('current_date', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        if available_slots:
            self.initial['available_slots'] = available_slots
        self.initial['date'] = current_date

    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'bike_count']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'bike_count': forms.NumberInput(attrs={'type': 'number'}),
        }

    def clean(self):
        """
        Custom validation for booking form fields.

        Example:
            Validate start and end times, slot availability, and equal ride
             duration.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        bikes = cleaned_data.get('bike_count')

        if start_time and end_time:
            start = start_time.strftime('%H:%M')
            end = end_time.strftime('%H:%M')
            desired_slot = (start, end)
            available_slots = self.initial.get('available_slots')
            current_date = self.initial.get('date')
            # validate time format
            if not validate_start_time(start_time, current_date):
                self.add_error(
                    'start_time',
                    _('Selected start time can\'t be in past')
                )
            # check if chosen time are available
            if not validate_slots(eval(available_slots), desired_slot):
                self.add_error(
                    'start_time',
                    _('Selected time is not available for booking')
                )
                self.add_error(
                    'end_time',
                    _('Selected time is not available for booking')
                )
            # check if ride time are equal 1 hour
            if not validate_equal_hour(start_time, end_time):
                self.add_error(
                    'end_time',
                    _('Common ride time must be equal to hour')
                )
            # validate bikes count
            if not validate_bikes(bikes):
                self.add_error(
                    'bike_count',
                    _('Bikes count must be at 1-4')
                )
        return cleaned_data


class BookingEditForm(forms.ModelForm):
    """
    Custom form for edit booking details.
    """
    def __init__(self, *args, **kwargs):
        slots = kwargs.pop('slots', None)
        date = kwargs.pop('date', None)
        super(BookingEditForm, self).__init__(*args, **kwargs)
        if slots:
            self.initial['slots'] = slots
        self.initial['date'] = date

    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'bike_count']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'bike_count': forms.NumberInput(attrs={'type': 'number'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        bikes = cleaned_data.get('bike_count')

        if start_time and end_time:
            start = start_time.strftime('%H:%M')
            end = end_time.strftime('%H:%M')
            desired_slot = (start, end)
            available_slots = self.initial.get('slots')
            current_date = self.initial.get('date')
            if not validate_start_time(start_time, current_date):
                self.add_error(
                    'start_time',
                    _('Selected start time can\'t be in past')
                )
            if not validate_slots(available_slots, desired_slot):
                self.add_error(
                    'start_time',
                    _('Selected time is not available for booking')
                )
                self.add_error(
                    'end_time',
                    _('Selected time is not available for booking')
                )
            if not validate_equal_hour(start_time, end_time):
                self.add_error(
                    'end_time',
                    _('Common ride time must be equal to hour')
                )
            if not validate_bikes(bikes):
                self.add_error(
                    'bike_count',
                    _('Bikes count must be at 1-4')
                )
        return cleaned_data


class BookingCancelForm(forms.ModelForm):
    """
    Custom form for cancel booking from profile page.

    Set status as canceled.
    """
    class Meta:
        model = Booking
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.HiddenInput()
        self.initial['status'] = _('canceled')
