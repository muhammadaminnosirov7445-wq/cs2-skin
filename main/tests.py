from django.test import TestCase

from .models import Case


class HomePageTests(TestCase):
    def test_empty_catalog_shows_admin_setup_links(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hozircha keyslar mavjud emas')
        self.assertContains(response, '/admin/main/item/add/')
        self.assertContains(response, '/admin/main/case/add/')

    def test_existing_case_is_rendered_instead_of_empty_state(self):
        case = Case.objects.create(name='Test case', price='10.00')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, case.name)
        self.assertNotContains(response, 'Hozircha keyslar mavjud emas')

