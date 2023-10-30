from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from phonenumber_field.formfields import PhoneNumberField

from .models import User


class UserRegistrationForm(UserCreationForm):

    name = forms.CharField(
        max_length=30,
        required=True,
        help_text=_('Required. No more than 30 characters')
    )

    email = forms.EmailField(
        max_length=50,
        required=True,
        help_text=_('Required. Enter a valid email address')
    )

    phone_number = PhoneNumberField(
        region='RU',
        required=True,
        help_text=_('Required. Enter a valid phone number')
    )

    class Meta:
        model = User
        fields = (
            'name',
            'email',
            'phone_number',
            'password1',
            'password2',
        )
