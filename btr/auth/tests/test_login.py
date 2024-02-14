from btr.test_init import BTRTestCase


class TestMultiplyLogin(BTRTestCase):

    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_login_with_username(self):
        response = self.client.post(
            self.login_url,
            data={'username': self.user.username, 'password': self.password},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'You are log in')
        self.assertTemplateUsed(response, 'index.html')

    def test_login_with_phone(self):
        response = self.client.post(
            self.login_url,
            data={
                'username': self.user.phone_number,
                'password': self.password
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'You are log in')
        self.assertTemplateUsed(response, 'index.html')

    def test_login_with_email(self):
        response = self.client.post(
            self.login_url,
            data={'username': self.user.email, 'password': self.password},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'You are log in')
        self.assertTemplateUsed(response, 'index.html')

    def test_login_with_name(self):
        response = self.client.post(
            self.login_url,
            data={'username': self.user.first_name, 'password': self.password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/auth.html')
