from django.test import TestCase

from apps.accounts.models import User
from apps.companies.tests.factories import PASSWORD, make_admin


class UserAdminTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)

    def test_django_admin_login_uses_the_email(self):
        self.client.logout()
        response = self.client.post('/django-admin/login/', {
            'username': self.admin.email, 'password': PASSWORD, 'next': '/django-admin/',
        })
        self.assertRedirects(response, '/django-admin/')

    def test_lists_load(self):
        for url in ['/django-admin/accounts/user/', '/django-admin/accounts/user/add/',
                    f'/django-admin/accounts/user/{self.admin.pk}/change/',
                    '/django-admin/companies/company/', '/django-admin/companies/vehicle/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_creates_a_user(self):
        response = self.client.post('/django-admin/accounts/user/add/', {
            'email': 'nouveau@b.tg', 'role': 'passenger', 'usable_password': 'true',
            'password1': PASSWORD, 'password2': PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.get(email='nouveau@b.tg').check_password(PASSWORD))

    def test_resets_a_password(self):
        user = User.objects.create_user(email='oubli@b.tg', password='ancien-mot-de-passe')
        response = self.client.post(f'/django-admin/accounts/user/{user.pk}/password/', {
            'usable_password': 'true', 'password1': PASSWORD, 'password2': PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.check_password(PASSWORD))
