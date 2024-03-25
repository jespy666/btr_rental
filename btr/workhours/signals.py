from django.db.models.signals import post_migrate
from django.dispatch import receiver


from .models import WorkHours


@receiver(post_migrate)
def initiate_default_hours(sender, **kwargs):
    if sender.name == 'btr.workhours':
        if not WorkHours.objects.exists():
            WorkHours.objects.create(
                day='Workday',
                open='11:00:00',
                close='22:00:00',
            )
            WorkHours.objects.create(
                day='Weekend',
                open='10:00:00',
                close='22:00:00',
            )
