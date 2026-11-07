# Gestion des véhicules

Le code se trouve dans `apps/companies` (modèle `Vehicle`, `forms/vehicle.py`, `views/vehicles.py`,
`api/vehicles.py`). Les pages et l'API sont réservées aux comptes compagnie, et chaque compagnie n'accède qu'à ses
propres véhicules.

## Fonctionnalités web

- Ajout d'un véhicule (immatriculation, marque et modèle, catégorie, places, équipements, visite technique,
  assurance, statut et observations).
- Recherche par immatriculation ou marque, filtres par statut et catégorie.
- Modification et suppression avec confirmation.
- Passage en maintenance et remise en service.
- Indicateurs calculés depuis les enregistrements.

## API JSON

| Méthode | URL | Fonction |
|---|---|---|
| GET, POST | `/compagnie/vehicules/api/` | Lister, créer |
| GET, PUT, PATCH, DELETE | `/compagnie/vehicules/api/<id>/` | Consulter, modifier, supprimer |

Ces routes utilisent la session Django. Les requêtes qui modifient des données doivent envoyer le cookie de session
et le jeton CSRF (en-tête `X-CSRFToken`), avec un corps JSON reprenant les champs du formulaire :

```json
{
  "registration_number": "TG-1234-BR",
  "brand_model": "Toyota Coaster",
  "category": "minibus",
  "seats": 30,
  "has_ac": true,
  "has_wifi": true,
  "has_usb": false,
  "technical_inspection_expiry": "2027-06-30",
  "insurance_policy_number": "POL-2027-001",
  "status": "active",
  "notes": ""
}
```

## Tests

```bash
python manage.py test apps.companies.tests.test_vehicles --settings=MutualTransport.settings.test
```
