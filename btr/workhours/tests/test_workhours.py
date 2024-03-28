from django.urls import reverse

from btr.fixtures_loader import load_json
from btr.test_init import BTRAdminTestCase
from btr.workhours.models import WorkHours


class TestWorkhours(BTRAdminTestCase):

    WORKHOURS_RECORDS = 2
    add = load_json('workhours/create.json')
    change = load_json('workhours/edit.json')

    def test_records_exists(self):
        self.assertEqual(WorkHours.objects.count(), self.WORKHOURS_RECORDS)

    def test_only_two_records(self):
        response = self.client.post(
            reverse('admin:workhours_workhours_add'), self.add, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WorkHours.objects.count(), self.WORKHOURS_RECORDS)

    def test_success_edit(self):
        response = self.client.post(
            reverse('admin:workhours_workhours_change', args=[1]),
            self.change)
        self.assertEqual(response.status_code, 302)
        workhours = WorkHours.objects.get(pk=1)
        open_hours = workhours.open.strftime('%H:%M:%S')
        self.assertEqual(self.change.get('open'), open_hours)
