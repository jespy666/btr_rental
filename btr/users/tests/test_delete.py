from django.urls import reverse_lazy

from btr.test_init import BTRTestCase
from btr.users.models import SiteUser


class TestUserDelete(BTRTestCase):

    def test_delete_yourself(self):
        response = self.client.post(
            reverse_lazy('user_delete', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(SiteUser.objects.count(), self.count - 1)

    def test_delete_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse_lazy('user_delete', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertEqual(SiteUser.objects.count(), self.count)

    def test_delete_other_user(self):
        response = self.client.post(
            reverse_lazy('user_delete', kwargs={'pk': 3})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(SiteUser.objects.count(), self.count)

    def test_delete_user_with_bookings(self):
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse_lazy('user_delete', kwargs={'pk': 2}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'Can\'t delete user with existed bookings'
        )
        self.assertTemplateUsed(
            response,
            'index.html'
        )
