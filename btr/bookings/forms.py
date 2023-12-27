from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import Booking


class BookingForm(forms.ModelForm):

    bike_count = forms.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ]
    )

    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'bike_count']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'bike_count': forms.NumberInput(attrs={'type': 'number'})
        }
