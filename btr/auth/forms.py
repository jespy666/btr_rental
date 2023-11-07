from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from phonenumber_field.formfields import PhoneNumberField

from .models import SiteUser, UserProfile


class UserRegistrationForm(UserCreationForm):

    username = forms.CharField(
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
            'email',
            'phone_number',
            'password1',
            'password2',
        )


class ProfileImageUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_image',)
