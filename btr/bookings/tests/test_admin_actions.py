from django.utils.translation import gettext as _

from btr.bookings.models import Booking
from btr.test_init import BTRAdminTestCase


class TestAdminBookings(BTRAdminTestCase):

    def test_multiply_accept(self):
        actions = self.model_admin.get_actions(self.request)
        make_confirm_action = actions['make_confirm'][0]
        make_confirm_action(
            self.model_admin,
            self.request,
            Booking.objects.filter(id__in=[self.booking.id, self.booking2.id])
        )
        self.booking.refresh_from_db()
        self.booking2.refresh_from_db()

        self.assertEqual(self.booking.status, _('confirmed'))
        self.assertEqual(self.booking2.status, _('confirmed'))

    def test_multiply_cancel(self):
        actions = self.model_admin.get_actions(self.request)
        make_confirm_action = actions['make_cancel'][0]
        make_confirm_action(
            self.model_admin,
            self.request,
            Booking.objects.filter(id__in=[self.booking.id, self.booking2.id])
        )
        self.booking.refresh_from_db()
        self.booking2.refresh_from_db()

        self.assertEqual(self.booking.status, _('canceled'))
        self.assertEqual(self.booking2.status, _('canceled'))
