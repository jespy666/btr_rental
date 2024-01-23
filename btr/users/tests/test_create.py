from django.urls import reverse_lazy

from btr.fixtures_loader import load_json
from btr.test_init import BTRTestCase
from btr.users.models import SiteUser


class TestUserCreate(BTRTestCase):
    create_url = reverse_lazy('registration')
    created_cases = load_json('users/create.json')

    def setUp(self):
        self.client.logout()

    def test_user_success_create(self):

        response = self.client.post(
            self.create_url,
            data=self.created_cases['valid']
        )

        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, self.login_url)
        self.assertEqual(SiteUser.objects.count(), self.count + 1)
