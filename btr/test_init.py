from django.test import TestCase
from django.urls import reverse_lazy
from django.utils.translation import activate

# from btr.bookings.models import Booking
from btr.users.models import SiteUser


class BTRTestCase(TestCase):

    fixtures = [
        'btr/fixtures/users/users.json',
    ]

    login_url = reverse_lazy('login')
    logout_url = reverse_lazy('logout')

    activate('en')

    count = 3

    def setUp(self):
        self.existed_username = SiteUser.objects.get(pk=1)
        self.existed_email = SiteUser.objects.get(pk=2)
        self.existed_phone = SiteUser.objects.get(pk=3)
        self.client.force_login(self.existed_username)
