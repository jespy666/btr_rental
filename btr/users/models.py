from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class SiteUser(AbstractUser):

    username = models.CharField(
        max_length=40,
        blank=False,
        verbose_name=_('Username, Phone or Email'),
        unique=True
    )

    first_name = models.CharField(
        max_length=40,
        blank=False,
        verbose_name=_('Name'),
        unique=False,
    )

    email = models.EmailField(
        max_length=50,
        blank=False,
        unique=True,
        verbose_name=_('Email')
    )

    phone_number = PhoneNumberField(
        blank=False,
        unique=True,
        verbose_name=_('Phone'),

    )

    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    LEVEL_CHOICES = [
        (_('Newbie'), _('Newbie')),
        (_('Amateur'), _('Amateur')),
        (_('Professional'), _('Professional')),
        (_('Master'), _('Master')),
    ]

    status = models.CharField(
        max_length=20,
        verbose_name=_('Level'),
        blank=True,
        unique=False,
        choices=LEVEL_CHOICES,
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
