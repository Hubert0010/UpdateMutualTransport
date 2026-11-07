import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.companies.forms.company import LOGO_MAX_SIZE

from .factories import make_company

MEDIA_ROOT = tempfile.mkdtemp()


def png_image(name='logo.png'):
    content = BytesIO()
    Image.new('RGB', (10, 10)).save(content, 'PNG')
    return SimpleUploadedFile(name, content.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompanyProfileTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.url = reverse('companies:profile')
        self.company = make_company(rccm='TG-LOM-2018-B-0421')
        self.client.force_login(self.company.user)

    def test_form_is_prefilled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['company'], self.company)
        self.assertEqual(response.context['form']['legal_name'].value(), 'NAGODE TRANSPORT SARL')

    def test_updates_the_information(self):
        response = self.client.post(self.url, {
            'legal_name': 'NAGODE & LOGISTIQUE SARL',
            'trade_name': 'NAGODE Transport',
            'support_phone': '+228 22 25 10 90',
            'tmoney_account': 'TM-NAGODE-88412',
        })
        self.assertRedirects(response, self.url)
        self.company.refresh_from_db()
        self.assertEqual(self.company.legal_name, 'NAGODE & LOGISTIQUE SARL')
        self.assertEqual(self.company.tmoney_account, 'TM-NAGODE-88412')

        messages = [str(m) for m in self.client.get(self.url).context['messages']]
        self.assertEqual(messages, ['Profil mis à jour avec succès.'])

    def test_admin_only_fields_cannot_be_changed(self):
        self.client.post(self.url, {'legal_name': 'X', 'rccm': 'PIRATE', 'nif': 'PIRATE', 'region': 'Kara'})
        self.company.refresh_from_db()
        self.assertEqual(self.company.legal_name, 'X')
        self.assertEqual(self.company.rccm, 'TG-LOM-2018-B-0421')
        self.assertEqual(self.company.nif, '')
        self.assertEqual(self.company.region, '')

    def test_only_the_logged_in_company_is_changed(self):
        other = make_company(email='autre@compagnie.tg', legal_name='AUTRE')
        self.client.post(self.url, {'legal_name': 'MODIFIEE', 'id': other.pk, 'user': other.user.pk})
        other.refresh_from_db()
        self.company.refresh_from_db()
        self.assertEqual(other.legal_name, 'AUTRE')
        self.assertEqual(self.company.legal_name, 'MODIFIEE')

    def test_invalid_form_saves_nothing(self):
        response = self.client.post(self.url, {'legal_name': '', 'support_phone': 'abc'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['form'].errors), {'legal_name', 'support_phone'})
        # Saisie conservée dans le formulaire, valeurs enregistrées dans `company`.
        self.assertEqual(response.context['form']['support_phone'].value(), 'abc')
        self.assertEqual(response.context['company'].legal_name, 'NAGODE TRANSPORT SARL')
        self.company.refresh_from_db()
        self.assertEqual(self.company.legal_name, 'NAGODE TRANSPORT SARL')

    def test_uploads_a_logo(self):
        self.client.post(self.url, {'legal_name': 'NAGODE', 'logo': png_image()})
        self.company.refresh_from_db()
        self.assertTrue(self.company.logo.name.startswith('companies/logos/logo'))
        self.assertTrue(self.company.logo.storage.exists(self.company.logo.name))

    def test_logo_is_kept_when_the_field_is_empty(self):
        self.client.post(self.url, {'legal_name': 'NAGODE', 'logo': png_image()})
        self.company.refresh_from_db()
        logo = self.company.logo.name
        self.client.post(self.url, {'legal_name': 'NAGODE'})
        self.company.refresh_from_db()
        self.assertEqual(self.company.logo.name, logo)

    def test_non_image_file_is_rejected(self):
        fake = SimpleUploadedFile('logo.svg', b'<svg onload="alert(1)"/>', content_type='image/svg+xml')
        response = self.client.post(self.url, {'legal_name': 'NAGODE', 'logo': fake})
        self.assertIn('logo', response.context['form'].errors)
        self.company.refresh_from_db()
        self.assertFalse(self.company.logo)

    def test_too_large_logo_is_rejected(self):
        too_large = SimpleUploadedFile(
            'logo.png', png_image().read() + b'\0' * LOGO_MAX_SIZE, content_type='image/png',
        )
        response = self.client.post(self.url, {'legal_name': 'NAGODE', 'logo': too_large})
        self.assertEqual(response.context['form'].errors['logo'], ['Le logo ne doit pas dépasser 2 Mo.'])
