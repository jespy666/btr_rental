from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext as _

from .models import Booking
from .validators import validate_slots, validate_start_time


class BookingForm(forms.ModelForm):

    bike_count = forms.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ]
    )

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
            _('start_time'): forms.TimeInput(attrs={'type': 'time'}),
            _('end_time'): forms.TimeInput(attrs={'type': 'time'}),
            _('bike_count'): forms.NumberInput(attrs={'type': 'number'})
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
        return cleaned_data
