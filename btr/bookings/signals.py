from django.db.models.signals import post_save
from django.db.models import Model
from django.dispatch import receiver
from django.utils.translation import gettext as _

from .models import Booking


@receiver(post_save, sender=Booking)
def update_user_status(sender: Model, instance: Booking, **kwargs) -> None:
    """
    Custom signal receiver to update user status based on completed bookings.

    Args:
        sender (Model): The model class that sends the signal
         (Booking in this case).
        instance (Booking): The specific booking instance that triggered
         the signal.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Example:
        When a booking is saved, this signal receiver checks the user's
         completed bookings count and updates their status accordingly
          (e.g., 'Newbie', 'Amateur', etc.). Exclude admin account.
    """
    rider = instance.rider
    # check if user are not admin
    if not rider.is_superuser:
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
