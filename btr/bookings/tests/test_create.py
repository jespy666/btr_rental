from django.urls import reverse_lazy

from btr.fixtures_loader import load_json
from btr.test_init import BTRTestCase
from ..models import Booking


class TestBookingCreate(BTRTestCase):
    create_url = reverse_lazy('book_create')
    cases = load_json('bookings/create.json')

    def test_success_create(self):
        post_data = self.cases['correct']
        slots = "[('10:00', '22:00')]"

        response = self.client.post(
            f"{self.create_url}?slots={slots}&selected_date="
            f"{post_data['booking_date']}",
            data=post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'Reservation created successfully'
        )
        self.assertTemplateUsed(
            response,
            'users/profile.html'
        )
        self.assertEqual(Booking.objects.count(), self.count + 1)

    def test_with_unauthenticated(self):
        self.client.logout()
        post_data = self.cases['correct']
        slots = "[('10:00', '22:00')]"

        response = self.client.post(
            f"{self.create_url}?slots={slots}&selected_date="
            f"{post_data['booking_date']}",
            data=post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'You must to be login to book ride'
        )
        self.assertTemplateUsed(
            response,
            'forms/auth.html'
        )
        self.assertEqual(Booking.objects.count(), self.count)

    def test_time_already_booked(self):
        post_data = self.cases['busy_time']
        slots = "[('10:00', '11:00')]"
        response = self.client.post(
            f"{self.create_url}?slots={slots}&selected_date="
            f"{post_data['booking_date']}",
            data=post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), self.count)

    def test_book_on_past(self):
        post_data = self.cases['past_date']
        date = '2000-January-03'
        slots = "[('10:00', '22:00')]"
        response = self.client.post(
            f"{self.create_url}?slots={slots}&selected_date={date}",
            data=post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), self.count)

    def test_bikes_overcounted(self):
        post_data = self.cases['to_many_bikes']
        slots = "[('10:00', '22:00')]"
        response = self.client.post(
            f"{self.create_url}?slots={slots}&selected_date="
            f"{post_data['booking_date']}",
            data=post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), self.count)
