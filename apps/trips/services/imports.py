"""Lecture et validation du fichier Excel de planning des voyages."""
import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo
SHEET_NAME = 'PLANNING_VOYAGE'
EXPECTED_COLUMNS = [
    'LIGNE_DEPART',
    'GARE_DEPART',
    'LIGNE_ARRIVEE',
    'GARE_ARRIVEE',
    'DATE_DEPART',
    'HEURE_DEPART',
    'DATE_ARRIVEE',
    'HEURE_ARRIVEE',
    'DUREE_TRAJET',
    'VILLE_LIEU_ESCALE',
    'PRIX_BILLET',
    'BUS_IMMAT',
    'NOMBRE_PLACES_BUS',
]
REQUIRED_COLUMNS = [column for column in EXPECTED_COLUMNS if column != 'BUS_IMMAT']


class InvalidImportFile(Exception):
    """Le fichier ne peut pas être analysé. Le message est destiné à l'utilisateur."""


@dataclass
class ImportResult:
    rows: list
    errors: list


def analyze_planning_file(file):
    """Analyse le fichier envoyé. Lève InvalidImportFile si son format n'est pas exploitable."""
    if not file:
        raise InvalidImportFile('Veuillez sélectionner un fichier Excel.')
    if not file.name.lower().endswith('.xlsx'):
        raise InvalidImportFile('Seuls les fichiers .xlsx sont acceptés.')
    if file.size > MAX_FILE_SIZE:
        raise InvalidImportFile('Le fichier dépasse la taille maximale de 10 Mo.')

    workbook = None
    try:
        workbook = load_workbook(file, read_only=True, data_only=True)
        return _analyze_workbook(workbook)
    except InvalidImportFile:
        raise
    except Exception as error:
        # openpyxl peut lever de nombreuses exceptions sur un fichier corrompu.
        logger.warning("Lecture impossible du fichier d'import %s", file.name, exc_info=True)
        raise InvalidImportFile(
            "Impossible de lire ce fichier Excel. Vérifiez qu'il s'agit d'un fichier .xlsx valide."
        ) from error
    finally:
        if workbook is not None:
            workbook.close()


def _analyze_workbook(workbook):
    if SHEET_NAME not in workbook.sheetnames:
        raise InvalidImportFile(f'La feuille {SHEET_NAME} est introuvable.')
    sheet = workbook[SHEET_NAME]

    headers = [
        str(cell.value).strip() if cell.value is not None else ''
        for cell in sheet[1]
    ]
    if headers != EXPECTED_COLUMNS:
        raise InvalidImportFile(
            'Les colonnes du fichier ne correspondent pas au modèle Excel officiel.'
        )

    rows = []
    errors = []
    for number, values in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if all(_is_blank(value) for value in values):
            continue
        data = dict(zip(EXPECTED_COLUMNS, values))
        errors.extend(_validate_row(number, data))
        rows.append({'numero': number, 'donnees': data})
    return ImportResult(rows=rows, errors=errors)


def _is_blank(value):
    return value is None or str(value).strip() == ''


def _validate_row(number, data):
    errors = []

    missing = [column for column in REQUIRED_COLUMNS if _is_blank(data.get(column))]
    if missing:
        errors.append(f'Ligne {number} : champs obligatoires manquants : ' + ', '.join(missing))

    price = data.get('PRIX_BILLET')
    if not _is_blank(price) and not _is_positive_price(price):
        errors.append(f'Ligne {number} : le prix doit être un nombre positif.')

    seats = data.get('NOMBRE_PLACES_BUS')
    if not _is_blank(seats) and not _is_positive_integer(seats):
        errors.append(f'Ligne {number} : le nombre de places doit être un entier positif.')

    return errors


def _is_positive_price(value):
    cleaned = str(value).upper().replace('FCFA', '').replace(' ', '').strip()
    try:
        price = Decimal(cleaned)
    except InvalidOperation:
        return False
    return price.is_finite() and price > 0


def _is_positive_integer(value):
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return False
    return number.is_finite() and number > 0 and number == number.to_integral_value()
