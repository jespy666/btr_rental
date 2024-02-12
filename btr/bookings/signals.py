from django.db.models.signals import post_save
from django.db.models import Model
from django.dispatch import receiver
from django.utils.translation import gettext as _

from .models import Booking


@receiver(post_save, sender=Booking)
def update_user_status(sender: Model, instance: Booking, **kwargs) -> None:
    """Setting the user level based on the number of rides"""
    rider = instance.rider
    book_count = rider.booking_set.filter(status='completed').count()
    match book_count:
        case count if count < 3:
            rider.status = _('Newbie')
        case count if 3 <= count < 5:
            rider.status = _('Amateur')
        case count if 5 <= count < 10:
            rider.status = _('Professional')
        case _:
            rider.status = _('Master')
    rider.save()
