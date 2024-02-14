from btr.test_init import BTRTestCase


class TestLogout(BTRTestCase):

    def test_logout(self):
        response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        message = messages[-1]
        self.assertEqual(message.tags, 'info')
        self.assertEqual(
            message.message,
            'You are logout',
        )
        self.assertTemplateUsed(response, 'index.html')
