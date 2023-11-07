from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from django.utils.translation import gettext as _


class SiteUser(AbstractUser):

    username = models.CharField(
        max_length=40,
        blank=False,
        verbose_name=_('Name, Phone or Email'),
        unique=False
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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(SiteUser, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )
