from django.urls import reverse_lazy

from btr.fixtures_loader import load_json
from btr.test_init import BTRTestCase
from btr.users.models import SiteUser


class TestUserCreate(BTRTestCase):
    create_url = reverse_lazy('registration')
    created_cases = load_json('users/create.json')

    def setUp(self):
        self.client.logout()

    def test_success_create(self):

        response = self.client.post(
            self.create_url,
            data=self.created_cases['valid']
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertEqual(SiteUser.objects.count(), self.count + 1)

    def test_success_flash(self):
        response = self.client.post(
            self.create_url,
            data=self.created_cases['valid'],
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(
            message.message,
            'User created successfully'
        )
        self.assertTemplateUsed(response, 'auth_form.html')

    def test_existed_username(self):
        response = self.client.post(
            self.create_url,
            data=self.created_cases['existed_username'],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_form.html')
        self.assertEqual(SiteUser.objects.count(), self.count)

    def test_existed_email(self):
        response = self.client.post(
            self.create_url,
            data=self.created_cases['existed_email'],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_form.html')
        self.assertEqual(SiteUser.objects.count(), self.count)

    def test_existed_phone(self):
        response = self.client.post(
            self.create_url,
            data=self.created_cases['existed_phone'],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_form.html')
        self.assertEqual(SiteUser.objects.count(), self.count)
