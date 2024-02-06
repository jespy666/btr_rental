from django.urls import reverse_lazy, reverse

from btr.test_init import BTRTestCase
from btr.fixtures_loader import load_json


class TestUserUpdate(BTRTestCase):
    update_case = load_json('users/update.json')

    def test_success_update(self):
        self.assertTrue(self.user.is_authenticated)
        response = self.client.post(
            reverse_lazy('user_edit', kwargs={'pk': 1}),
            data=self.update_case
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('profile', kwargs={'pk': 1})
        )

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse_lazy('user_edit', kwargs={'pk': 1}),
            data=self.update_case,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'You must to be log in'
        )
        self.assertTemplateUsed(response, 'forms/auth.html')

    def test_update_other_user(self):
        response = self.client.post(
            reverse_lazy('user_edit', kwargs={'pk': 2}),
            data=self.update_case,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'You can\'t edit other user profile!'
        )
        self.assertTemplateUsed(response, 'index.html')
