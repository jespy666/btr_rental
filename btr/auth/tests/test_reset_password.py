from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from btr.test_init import BTRTestCase


class TestResetPassword(BTRTestCase):

    confirm_code_url = reverse_lazy('confirm')

    def setUp(self):
        super().setUp()
        self.client.logout()
        self.response = self.client.post(
            reverse_lazy('auth-reset'),
            data={'email': self.user.email},
        )

    def test_success_reset(self):
        code = self.client.session.get('verification_code')
        response = self.client.post(
            self.confirm_code_url,
            data={'code': code},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        message = messages[-1]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'Your password was successfully reset!\n'
            'New password was send on your email',
        )
        self.assertTemplateUsed(response, 'forms/auth.html')

    def test_wrong_code(self):
        response = self.client.post(
            self.confirm_code_url,
            data={'code': 'wrong-code'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        message = messages[-1]
        self.assertEqual(message.tags, 'error')
        self.assertEqual(
            message.message,
            _('Verification codes not match'),
        )
        self.assertTemplateUsed(
            response,
            'forms/confirm_code.html'
        )
