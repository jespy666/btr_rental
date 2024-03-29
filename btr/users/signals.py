from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from .models import SiteUser


@receiver(post_save, sender=SiteUser)
def set_status(sender: Model, instance: SiteUser,
               created: bool, **kwargs) -> None:
    """
    Signal handler to set status to new users.

    Args:
        sender (Model): The sender model class.
        instance (SiteUser): The instance of the user being saved.
        created (bool): A flag indicating whether the instance was
         created or updated.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created:
        instance.status = _('newbie')
        instance.save()
