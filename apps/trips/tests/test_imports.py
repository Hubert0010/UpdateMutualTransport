from datetime import date, time
from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from openpyxl import Workbook

from apps.companies.tests.factories import make_company
from apps.trips.services.imports import EXPECTED_COLUMNS, MAX_FILE_SIZE, SHEET_NAME


def valid_row(**overrides):
    row = dict(zip(EXPECTED_COLUMNS, [
        'Lomé', 'Agoè', 'Atakpamé', 'Gare centrale', date(2027, 1, 11), time(9, 0), date(2027, 1, 11), time(14, 0),
        '5h', 'Tsévié', '4500 FCFA', 'TG-1234-BR', 32,
    ]))
    row.update(overrides)
    return [row[column] for column in EXPECTED_COLUMNS]


def excel_file(rows=(), headers=EXPECTED_COLUMNS, sheet=SHEET_NAME, name='planning.xlsx'):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet
    worksheet.append(list(headers))
    for row in rows:
        worksheet.append(row)
    content = BytesIO()
    workbook.save(content)
    return SimpleUploadedFile(name, content.getvalue())


class PlanningImportTests(TestCase):
    def setUp(self):
        self.url = reverse('trips:import')
        self.client.force_login(make_company().user)

    def upload(self, file):
        return self.client.post(self.url, {'fichier_excel': file} if file else {})

    def assert_error(self, file, message):
        response = self.upload(file)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['erreur'], message)

    def test_page_displays(self):
        self.assertTemplateUsed(self.client.get(self.url), 'core/compagnie/import_donnees.html')

    def test_missing_file(self):
        self.assert_error(None, 'Veuillez sélectionner un fichier Excel.')

    def test_wrong_extension(self):
        self.assert_error(SimpleUploadedFile('planning.csv', b'a,b'), 'Seuls les fichiers .xlsx sont acceptés.')

    def test_too_large_file(self):
        self.assert_error(
            SimpleUploadedFile('planning.xlsx', b'0' * (MAX_FILE_SIZE + 1)),
            'Le fichier dépasse la taille maximale de 10 Mo.',
        )

    def test_corrupted_file(self):
        with self.assertLogs('apps.trips.services.imports', level='WARNING'):
            self.assert_error(
                SimpleUploadedFile('planning.xlsx', b'pas un fichier excel'),
                "Impossible de lire ce fichier Excel. Vérifiez qu'il s'agit d'un fichier .xlsx valide.",
            )

    def test_missing_sheet(self):
        self.assert_error(excel_file(sheet='AUTRE'), 'La feuille PLANNING_VOYAGE est introuvable.')

    def test_wrong_columns(self):
        self.assert_error(
            excel_file(headers=['A', 'B']),
            'Les colonnes du fichier ne correspondent pas au modèle Excel officiel.',
        )

    def test_valid_file(self):
        response = self.upload(excel_file([valid_row(), valid_row()]))
        self.assertEqual(response.context['nombre_lignes'], 2)
        self.assertEqual(response.context['erreurs'], [])
        self.assertEqual(response.context['nom_fichier'], 'planning.xlsx')
        self.assertIn('succes', response.context)
        self.assertEqual(response.context['apercu'][0]['numero'], 2)
        self.assertContains(response, 'Agoè')

    def test_preview_is_limited_but_all_rows_are_counted(self):
        response = self.upload(excel_file([valid_row()] * 12))
        self.assertEqual(response.context['nombre_lignes'], 12)
        self.assertEqual(len(response.context['apercu']), 10)

    def test_empty_rows_are_ignored(self):
        response = self.upload(excel_file([valid_row(), [None] * 13, valid_row()]))
        self.assertEqual(response.context['nombre_lignes'], 2)

    def test_vehicle_plate_is_optional(self):
        response = self.upload(excel_file([valid_row(BUS_IMMAT=None)]))
        self.assertEqual(response.context['erreurs'], [])

    def test_row_errors_are_reported(self):
        response = self.upload(excel_file([
            valid_row(GARE_DEPART=None, DUREE_TRAJET=None),
            valid_row(PRIX_BILLET='gratuit'),
            valid_row(PRIX_BILLET=-5),
            valid_row(NOMBRE_PLACES_BUS=2.5),
        ]))
        self.assertEqual(response.context['erreurs'], [
            'Ligne 2 : champs obligatoires manquants : GARE_DEPART, DUREE_TRAJET',
            'Ligne 3 : le prix doit être un nombre positif.',
            'Ligne 4 : le prix doit être un nombre positif.',
            'Ligne 5 : le nombre de places doit être un entier positif.',
        ])
        self.assertNotIn('succes', response.context)

    def test_official_template_is_accepted(self):
        path = settings.BASE_DIR / 'MutualTransport' / 'static' / 'fichiers' / 'Modele_Import_MutualTransport.xlsx'
        response = self.upload(SimpleUploadedFile(path.name, path.read_bytes()))
        self.assertNotIn('erreur', response.context)

    def test_template_download(self):
        response = self.client.get(reverse('trips:import_template'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Modele_Import_MutualTransport.xlsx', response['Content-Disposition'])
        response.close()
