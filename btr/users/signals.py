from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from .models import SiteUser


@receiver(post_save, sender=SiteUser)
def set_status(sender: Model, instance: SiteUser,
               created: bool, **kwargs) -> None:
    """Set status to new users"""
    if created:
        instance.status = _('newbie')
        instance.save()
