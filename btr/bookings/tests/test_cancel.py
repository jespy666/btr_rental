from django.urls import reverse
from django.utils.translation import gettext as _

from btr.test_init import BTRTestCase


class TestCancelBooking(BTRTestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user2)

    def test_success(self):
        response = self.client.post(
            reverse('book_cancel', kwargs={'pk': 2}),
            data={'status': _('canceled')},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'You are canceled the ride'
        )
        self.assertTemplateUsed(
            response,
            'users/profile.html'
        )

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse('book_cancel', kwargs={'pk': 2}),
            data={'status': _('canceled')},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'You must to be Log In'
        )
        self.assertTemplateUsed(
            response,
            'forms/auth.html'
        )
