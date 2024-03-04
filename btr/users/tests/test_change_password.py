from django.urls import reverse_lazy

from btr.test_init import BTRTestCase
from btr.fixtures_loader import load_json


class TestUserChangePassword(BTRTestCase):
    change_pswd_cases = load_json('users/change_password.json')

    def test_success_change(self):
        self.assertTrue(self.user.is_authenticated)
        response = self.client.post(
            reverse_lazy('change_password', kwargs={'pk': 1}),
            data=self.change_pswd_cases['valid'],
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'Password changed successfully'
        )
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_wrong_old_password(self):
        response = self.client.post(
            reverse_lazy('change_password', kwargs={'pk': 1}),
            data=self.change_pswd_cases['wrong_old_password'],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/change_password.html')

    def test_passwords_not_match(self):
        response = self.client.post(
            reverse_lazy('change_password', kwargs={'pk': 1}),
            data=self.change_pswd_cases['do_not_match'],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/change_password.html')
