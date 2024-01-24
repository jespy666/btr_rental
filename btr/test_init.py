from django.db.models.signals import post_save
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils.translation import activate

from btr.bookings.models import Booking
from btr.users.models import SiteUser
from btr.bookings.signals import booking_confirm_notify, create_booking_notify


class BTRTestCase(TestCase):

    post_save.disconnect(booking_confirm_notify, sender=Booking)
    post_save.disconnect(create_booking_notify, sender=Booking)

    fixtures = [
        'btr/fixtures/users/users.json',
        'btr/fixtures/bookings/bookings.json',
    ]

    home_url = reverse_lazy('home')
    login_url = reverse_lazy('login')
    logout_url = reverse_lazy('logout')

    activate('en')

    count = 3

    def setUp(self):
        self.user = SiteUser.objects.get(pk=1)
        self.user2 = SiteUser.objects.get(pk=2)
        self.user3 = SiteUser.objects.get(pk=3)

        self.booking = Booking.objects.get(pk=1)

        self.client.force_login(self.user)
