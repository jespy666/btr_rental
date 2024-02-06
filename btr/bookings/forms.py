from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Booking
from .validators import (validate_slots, validate_start_time,
                         validate_equal_hour)


class BookingForm(forms.ModelForm):

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
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            start = start_time.strftime('%H:%M')
            end = end_time.strftime('%H:%M')
            desired_slot = (start, end)
            available_slots = self.initial.get('available_slots')
            current_date = self.initial.get('date')
            if not validate_start_time(start_time, current_date):
                self.add_error(
                    'start_time',
                    _('Selected start time can\'t be in past')
                )
            if not validate_slots(eval(available_slots), desired_slot):
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
        return cleaned_data


class BookingEditForm(forms.ModelForm):

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
        return cleaned_data


class BookingCancelForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.HiddenInput()
        self.initial['status'] = _('canceled')
