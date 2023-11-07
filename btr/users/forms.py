from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext as _

from btr.users.models import SiteUser


class UserRegistrationForm(UserCreationForm):

    username = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Unique. No more than 40 characters')
    )

    first_name = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Required. No more than 40 characters')
    )

    email = forms.EmailField(
        max_length=50,
        required=True,
        help_text=_('Required. Enter a valid email address')
    )

    phone_number = PhoneNumberField(
        region='RU',
        required=True,
        help_text=_('Required. Enter a valid phone number'),
        widget=forms.TextInput(attrs={'id': 'id_phone_number'})
    )

    class Meta:
        model = SiteUser
        fields = (
            'username',
            'first_name',
            'email',
            'phone_number',
            'password1',
            'password2',
        )


class UserEditForm(UserCreationForm):
    username = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Unique. No more than 40 characters')
    )

    first_name = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Required. No more than 40 characters')
    )

    email = forms.EmailField(
        max_length=50,
        required=True,
        help_text=_('Required. Enter a valid email address')
    )

    phone_number = PhoneNumberField(
        region='RU',
        required=True,
        help_text=_('Required. Enter a valid phone number'),
        widget=forms.TextInput(attrs={'id': 'id_phone_number'})
    )

    class Meta:
        model = SiteUser
        fields = (
            'username',
            'first_name',
            'email',
            'phone_number',
            'password1',
            'password2',
        )

    def clean_username(self):
        return self.cleaned_data.get("username")
