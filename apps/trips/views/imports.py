"""Import du planning des voyages depuis un fichier Excel."""
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render

from apps.accounts.decorators import company_required

from ..services.imports import InvalidImportFile, analyze_planning_file

PREVIEW_SIZE = 10
TEMPLATE_FILE_NAME = 'Modele_Import_MutualTransport.xlsx'


@company_required
def import_planning(request):
    """Réception, lecture et validation du fichier Excel."""
    context = {}

    if request.method == 'POST':
        file = request.FILES.get('fichier_excel')
        try:
            result = analyze_planning_file(file)
        except InvalidImportFile as error:
            context['erreur'] = str(error)
        else:
            context.update({
                'apercu': result.rows[:PREVIEW_SIZE],
                'nombre_lignes': len(result.rows),
                'erreurs': result.errors,
                'nom_fichier': file.name,
            })
            if not result.errors:
                context['succes'] = (
                    'Les champs obligatoires et les premières vérifications sont corrects.'
                )

    return render(request, 'core/compagnie/import_donnees.html', context)


@company_required
def download_import_template(request):
    """Télécharge le modèle Excel vierge."""
    path = Path(settings.BASE_DIR) / 'MutualTransport' / 'static' / 'fichiers' / TEMPLATE_FILE_NAME
    if not path.is_file():
        raise Http404('Le modèle Excel est introuvable.')
    return FileResponse(path.open('rb'), as_attachment=True, filename=TEMPLATE_FILE_NAME)
