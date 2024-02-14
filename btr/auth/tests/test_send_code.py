from django.urls import reverse_lazy

from btr.test_init import BTRTestCase


class TestSendVerificationCode(BTRTestCase):

    reset_url = reverse_lazy('auth-reset')

    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_send_with_non_exist_user(self):
        response = self.client.post(
            self.reset_url,
            data={'email': 'non-exist@mail.com'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            'User with this email does not exist',
        )
        self.assertTemplateUsed(
            response,
            'forms/password_reset.html'
        )

    def test_send_success(self):
        response = self.client.post(
            self.reset_url,
            data={'email': self.user.email},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'Verification code was send to your email',
        )
        self.assertTemplateUsed(
            response,
            'forms/confirm_code.html'
        )
