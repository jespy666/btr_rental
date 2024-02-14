from django.urls import reverse

from btr.fixtures_loader import load_json
from btr.test_init import BTRTestCase


class TestBookingEdit(BTRTestCase):

    edit_cases = load_json('bookings/edit.json')

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user2)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse('book_edit', kwargs={'pk': self.booking.pk}),
            self.edit_cases['correct'],
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'You must to be login to edit bookings',
        )
        self.assertTemplateUsed(
            response,
            'forms/auth.html',
        )

    def test_edit_only_bikes(self):
        response = self.client.post(
            reverse('book_edit', kwargs={'pk': 1}),
            self.edit_cases['same_time'],
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'Reservation change successfully',
        )
        self.assertTemplateUsed(
            response,
            'users/profile.html',
        )

    def test_with_same_start(self):
        response = self.client.post(
            reverse('book_edit', kwargs={'pk': 1}),
            self.edit_cases['same_start'],
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'Reservation change successfully',
        )
        self.assertTemplateUsed(
            response,
            'users/profile.html',
        )

    def test_with_overcounted_bikes(self):
        response = self.client.post(
            reverse('book_edit', kwargs={'pk': 1}),
            self.edit_cases['to_many_bikes'],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/book_edit.html')
