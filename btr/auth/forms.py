from django import forms
from django.utils.translation import gettext as _


class AuthPasswordResetForm(forms.Form):
    help_text = _(
        'Write your valid email where the confirmation code will be sent'
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={'autocomplete': 'email', 'placeholder': help_text}
        ),
        label=_('Email'),
    )


class AuthConfirmForm(forms.Form):
    help_text = _(
        'Type verification code from email'
    )
    code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': help_text}),
        label=_('Verification Code'),
    )
