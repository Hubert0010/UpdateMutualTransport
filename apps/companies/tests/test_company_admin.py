from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company

from .factories import make_admin, make_company


class CompanyAccountCreationTests(TestCase):
    def setUp(self):
        self.url = reverse('companies:admin_list')
        self.client.force_login(make_admin())

    def create(self, **fields):
        return self.client.post(self.url, {
            'legal_name': 'SAVANES EXPRESS SARL', 'email': 'contact@savanes.tg', **fields,
        })

    def test_generated_credentials_allow_login(self):
        response = self.create(rccm='TG-DAP-2024-B-0192', region='Savanes', city='Dapaong')
        self.assertEqual(response.status_code, 200)
        credentials = response.context['credentials']
        self.assertEqual(credentials['email'], 'contact@savanes.tg')

        company = Company.objects.get(user__email='contact@savanes.tg')
        self.assertEqual(company.rccm, 'TG-DAP-2024-B-0192')
        self.assertEqual(company.user.role, User.Role.COMPANY)
        self.assertFalse(company.user.is_staff)
        self.assertNotIn(credentials['password'], company.user.password)

        self.client.logout()
        response = self.client.post('/connexion/', {
            'email': credentials['email'], 'password': credentials['password'],
        })
        self.assertRedirects(response, reverse('core:compagnie_dashboard'))

    def test_response_with_the_password_is_not_cached(self):
        self.assertIn('no-store', self.create()['Cache-Control'])

    def test_email_already_used_is_rejected_ignoring_case(self):
        make_company(email='contact@savanes.tg')
        response = self.create(email='CONTACT@savanes.tg')
        self.assertIn('email', response.context['form'].errors)
        self.assertIsNone(response.context['credentials'])
        self.assertEqual(Company.objects.count(), 1)

    def test_required_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(set(response.context['form'].errors), {'legal_name', 'email'})
        self.assertFalse(User.objects.filter(role=User.Role.COMPANY).exists())

    def test_list_contains_the_companies(self):
        company = make_company()
        self.assertEqual(list(self.client.get(self.url).context['companies']), [company])

    def test_company_cannot_create_an_account(self):
        self.client.force_login(make_company().user)
        self.assertEqual(self.create().status_code, 403)
        self.assertFalse(Company.objects.filter(user__email='contact@savanes.tg').exists())
