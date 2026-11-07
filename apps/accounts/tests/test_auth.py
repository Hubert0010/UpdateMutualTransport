from django.test import TestCase
from django.urls import reverse

from apps.companies.tests.factories import PASSWORD, make_admin, make_company


class LoginTests(TestCase):
    url = '/connexion/'

    def login(self, email, password=PASSWORD, **extra):
        return self.client.post(self.url, {'email': email, 'password': password, **extra})

    def test_company_lands_on_its_dashboard(self):
        make_company()
        self.assertRedirects(self.login('contact@nagode.tg'), reverse('core:compagnie_dashboard'))

    def test_email_ignores_case(self):
        make_company()
        self.assertRedirects(self.login('CONTACT@Nagode.tg'), reverse('core:compagnie_dashboard'))

    def test_admin_lands_on_its_dashboard(self):
        make_admin()
        self.assertRedirects(self.login('admin@mutualtransport.tg'), reverse('core:admin_dashboard'))

    def test_root_url_shows_the_login_page(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'core/login.html')

    def test_wrong_password_and_unknown_email_give_the_same_error(self):
        make_company()
        for response in (self.login('contact@nagode.tg', 'faux'), self.login('inconnu@nagode.tg')):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context['form'].non_field_errors(),
                ['Adresse e-mail ou mot de passe incorrect.'],
            )
            self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_account_is_rejected(self):
        company = make_company()
        company.user.is_active = False
        company.user.save()
        self.login('contact@nagode.tg')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_remember_me_keeps_the_session(self):
        make_company()
        self.login('contact@nagode.tg', remember='on')
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_without_remember_me_session_ends_with_the_browser(self):
        make_company()
        self.login('contact@nagode.tg')
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_internal_next_is_followed_but_not_external(self):
        make_company()
        profile = reverse('companies:profile')
        self.assertRedirects(self.login('contact@nagode.tg', next=profile), profile)

        self.client.post(reverse('accounts:logout'))
        response = self.login('contact@nagode.tg', next='https://exemple.com/piege')
        self.assertRedirects(response, reverse('core:compagnie_dashboard'))

    def test_logged_in_user_is_sent_to_its_space(self):
        self.client.force_login(make_company().user)
        self.assertRedirects(self.client.get(self.url), reverse('core:compagnie_dashboard'))

    def test_logout_is_post_only(self):
        self.client.force_login(make_company().user)
        url = reverse('accounts:logout')

        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

        self.assertRedirects(self.client.post(url), reverse('accounts:login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_registration_route_no_longer_exists(self):
        self.assertEqual(self.client.get('/inscription/').status_code, 404)
