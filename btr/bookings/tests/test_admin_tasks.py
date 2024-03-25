from unittest.mock import patch
from django.utils.translation import gettext as _

from btr.test_init import BTRAdminTestCase, TestForm


class TestAdminTasks(BTRAdminTestCase):

    @patch('btr.bookings.admin.send_vk_notify.delay')
    @patch('btr.bookings.admin.send_confirm_message.delay')
    @patch('btr.bookings.admin.send_cancel_message.delay')
    def test_confirm_booking(self, send_cancel, send_confirm, send_vk_notify):
        form_data = {
            'rider': self.user,
            'status': _('confirmed'),
            'booking_date': '2024-02-15',
            'start_time': '18:00',
            'end_time': '19:00',
            'bike_count': 2,
        }

        form = TestForm(form_data)
        obj = form.save(commit=False)
        obj.save()
        self.model_admin.save_model(
            obj=self.booking,
            request=self.request,
            form=form,
            change=True
        )
        send_vk_notify.assert_called_once()
        # send_confirm.assert_called_once()
        send_cancel.assert_not_called()

    @patch('btr.bookings.admin.send_vk_notify.delay')
    @patch('btr.bookings.admin.send_confirm_message.delay')
    @patch('btr.bookings.admin.send_cancel_message.delay')
    def test_cancel_booking(self, send_cancel, send_confirm, send_vk_notify):
        form_data = {
            'rider': self.user,
            'status': _('canceled'),
            'booking_date': '2024-02-15',
            'start_time': '18:00',
            'end_time': '19:00',
            'bike_count': 2,
        }

        form = TestForm(form_data)
        obj = form.save(commit=False)
        obj.save()
        self.model_admin.save_model(
            obj=self.booking,
            request=self.request,
            form=form,
            change=True
        )
        send_vk_notify.assert_called_once()
        send_confirm.assert_not_called()
        # send_cancel.assert_called_once()
