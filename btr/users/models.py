from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
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

    def __str__(self):
        return self.username
