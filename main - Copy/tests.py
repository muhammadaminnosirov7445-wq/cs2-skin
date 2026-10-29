from django.test import RequestFactory, TestCase
from django.urls import reverse

from main.views import open_case
from store.models import DemoCase


class DemoCaseCatalogTests(TestCase):
    def test_legacy_case_open_endpoint_cannot_change_a_real_balance(self):
        response = open_case(RequestFactory().post('/open/1/'), case_id=1)
        self.assertEqual(response.status_code, 410)

    def test_empty_catalog_shows_filter_empty_state(self):
        response = self.client.get(reverse('store:demo_cases'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No cases match those filters')

    def test_existing_case_is_rendered_instead_of_empty_state(self):
        case = DemoCase.objects.create(
            name='Test case',
            slug='test-case',
            description='A local demo case.',
            category='Neon',
            theme='Aurora',
            cover_image='demo/cases/test-case.svg',
            demo_price='10.00',
        )
        response = self.client.get(reverse('store:demo_cases'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, case.name)
        self.assertNotContains(response, 'No cases match those filters')
 