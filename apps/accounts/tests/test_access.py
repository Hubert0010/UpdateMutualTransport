from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.tests.factories import PASSWORD, make_admin, make_company

ADMIN_PAGES = [
    'core:admin_dashboard', 'companies:admin_list', 'core:admin_utilisateurs',
    'core:admin_reservations', 'core:admin_collecte',
]
COMPANY_PAGES = [
    'core:compagnie_dashboard', 'vehicles:list', 'vehicles:create', 'vehicles:api',
    'core:compagnie_trajets', 'core:compagnie_reservations', 'companies:profile', 'core:compagnie_regles',
    'trips:import', 'trips:import_template',
]


class AccessControlTests(TestCase):
    def assert_status(self, pages, status):
        for name in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, status)
                response.close()

    def test_anonymous_is_redirected_to_login(self):
        for name in ADMIN_PAGES + COMPANY_PAGES:
            url = reverse(name)
            with self.subTest(page=name):
                self.assertRedirects(self.client.get(url), f'/connexion/?next={url}')

    def test_company_reaches_its_space_only(self):
        self.client.force_login(make_company().user)
        self.assert_status(COMPANY_PAGES, 200)
        self.assert_status(ADMIN_PAGES, 403)

    def test_admin_reaches_its_space_only(self):
        self.client.force_login(make_admin())
        self.assert_status(ADMIN_PAGES, 200)
        self.assert_status(COMPANY_PAGES, 403)

    def test_passenger_reaches_neither_space(self):
        self.client.force_login(User.objects.create_user(email='voyageur@b.tg', password=PASSWORD))
        self.assert_status(ADMIN_PAGES + COMPANY_PAGES, 403)

    def test_company_role_without_company_is_rejected(self):
        self.client.force_login(
            User.objects.create_user(email='orphelin@b.tg', password=PASSWORD, role=User.Role.COMPANY)
        )
        self.assert_status(['companies:profile'], 403)
