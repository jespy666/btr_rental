from django import forms
from django.contrib.admin import AdminSite
from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy
from django.utils.translation import activate

from btr.bookings.admin import BookingAdmin
from btr.bookings.models import Booking
from btr.users.models import SiteUser


class BTRTestCase(TestCase):

    fixtures = [
        'btr/fixtures/users/users.json',
        'btr/fixtures/bookings/bookings.json',
    ]

    home_url = reverse_lazy('home')
    login_url = reverse_lazy('login')
    logout_url = reverse_lazy('logout')

    password = 'qwertycvbn'

    activate('en')

    count = 3

    def setUp(self):

        self.user = SiteUser.objects.get(pk=1)
        self.user.set_password(self.password)
        self.user.save()

        self.user2 = SiteUser.objects.get(pk=2)
        self.user3 = SiteUser.objects.get(pk=3)

        self.booking = Booking.objects.get(pk=1)
        self.booking2 = Booking.objects.get(pk=2)

        self.client.force_login(self.user)


class BTRAdminTestCase(BTRTestCase):

    def setUp(self):
        super().setUp()
        self.admin = SiteUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )
        self.site = AdminSite()
        self.model_admin = BookingAdmin(Booking, self.site)
        self.client.force_login(self.admin)
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')
        self.request.user = self.admin


class TestForm(forms.ModelForm):

    status = forms.CharField()

    class Meta:
        model = Booking
        fields = '__all__'
