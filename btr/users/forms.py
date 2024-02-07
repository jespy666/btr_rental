from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext as _

from btr.users.models import SiteUser


class UserRegistrationForm(UserCreationForm):

    username = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Unique. No more than 40 characters'),
        label=_('Username'),
        label_suffix='*',
    )

    first_name = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Required. No more than 40 characters'),
        label=_('Name'),
        label_suffix='*',
    )

    email = forms.EmailField(
        max_length=50,
        required=True,
        help_text=_('Required. Enter a valid emails address'),
        label=_('Email'),
        label_suffix='*',
    )

    phone_number = PhoneNumberField(
        region='RU',
        required=True,
        help_text=_('Required. Enter a valid phone number'),
        widget=forms.TextInput(attrs={'id': 'id_phone_number'}),
        label=_('Phone'),
        label_suffix='*',
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


class UserEditProfileImageForm(forms.ModelForm):

    profile_image = forms.ImageField(
        required=False,
        label=_('Photo'),
    )

    class Meta:
        model = SiteUser
        fields = ['profile_image']


class UserEditForm(forms.ModelForm):

    username = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Unique. No more than 40 characters'),
        label=_('Username'),
        label_suffix='*',
    )

    first_name = forms.CharField(
        max_length=40,
        required=True,
        help_text=_('Required. No more than 40 characters'),
        label=_('Name'),
        label_suffix='*',
    )

    email = forms.EmailField(
        max_length=50,
        required=True,
        help_text=_('Required. Enter a valid emails address'),
        label=_('Email'),
        label_suffix='*',
    )

    phone_number = PhoneNumberField(
        region='RU',
        required=True,
        help_text=_('Required. Enter a valid phone number'),
        widget=forms.TextInput(attrs={'id': 'id_phone_number'}),
        label=_('Phone'),
        label_suffix='*',
    )

    class Meta:
        model = SiteUser
        fields = (
            'username',
            'first_name',
            'email',
            'phone_number',
        )


class ChangePasswordForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Enter your current password')
            }
        )
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Enter a new password')
            }
        )
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Enter a new password again')
            }
        )
