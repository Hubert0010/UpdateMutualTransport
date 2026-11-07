# MutualTransport — Backend

Plateforme de mutualisation du transport interurbain au Togo. Ce dépôt contient le backend Django et la
plateforme web des compagnies et de l'administrateur. L'application mobile Flutter des voyageurs consommera
l'API REST du backend.

## Installation

Prérequis : Python 3.12 ou plus récent.

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # la connexion se fait par e-mail
python manage.py runserver
```

## Structure

```
MutualTransport/        Configuration du projet, sans logique métier
├── settings/           base, dev, test, staging, prod
├── static/             Fichiers statiques du frontend
├── urls.py             Routage principal, un include par app
└── api_v1.py           Routage de l'API, un include par app
core/                   Socle partagé : modèles abstraits, gabarits, pages encore statiques
apps/                   Un dossier par domaine métier
docs/                   Documentation des modules
```

| App | Responsabilité | État |
|---|---|---|
| `accounts` | Utilisateurs, rôles, connexion | Connexion et déconnexion en place |
| `companies` | Compagnies, profil, flotte | Création de compte, profil et véhicules en place |
| `trips` | Trajets, recherche, correspondances, import | Analyse du fichier Excel en place, trajets à faire |
| `bookings` | Réservations, places, billets | À faire |
| `payments` | Paiements Mobile Money et carte | À faire |
| `notifications` | E-mail, SMS, push | À faire |
| `assistant` | Chatbot, relais vers un conseiller | À faire |
| `supervision` | Tableaux de bord, supervision administrateur | À faire |

## Où mettre le code

Toutes les apps ont la même structure :

| Emplacement | Contenu |
|---|---|
| `models/` | Un fichier par modèle, chaque modèle étant exporté dans `models/__init__.py` |
| `forms/` | Validation des formulaires web |
| `views/` | Pages web : lecture de la requête, appel d'un service, réponse |
| `api/` | Endpoints de l'API REST : `serializers.py`, vues et `urls.py` |
| `services/` | Logique métier, partagée par `views/` et `api/` |
| `tests/` | Un fichier `test_*.py` par sujet |
| `templates/` | Gabarits propres à l'app |
| `urls.py`, `admin.py` | Routes et administration Django de l'app |

## Conventions

- **Langue :** code en anglais (apps, modèles, champs, fonctions) ; interface, messages et URLs en français.
- **Dépendances entre apps :** `accounts` ← `companies` ← `trips` ← `bookings` ← `payments`. Une app ne doit pas
  importer une app située à sa droite, afin d'éviter les dépendances circulaires entre modèles et migrations.
- **Logique métier :** elle va dans `services/`, pas dans les vues. L'API pourra ainsi la réutiliser.
- **Contrôle d'accès :** chaque vue d'un espace utilise `admin_required` ou `company_required`
  (`apps/accounts/decorators.py`). Les données d'une compagnie sont toujours lues à partir de
  `request.user.company`, jamais à partir d'un identifiant envoyé par le client.
- **Utilisateur :** référencer `settings.AUTH_USER_MODEL` dans les modèles. La date de création et de modification
  s'obtient en héritant de `core.models.TimeStampedModel`.
- **Routes :** elles sont déclarées dans le `urls.py` de l'app. `MutualTransport/urls.py` et `INSTALLED_APPS`
  n'ont pas à changer pour une nouvelle fonctionnalité.
- **Gabarits :** ils sont gérés par le développeur frontend. Une modification du backend ne doit pas les changer, et
  les noms de routes qu'ils utilisent doivent rester disponibles. `core/tests/` vérifie ce point.

## API REST

L'API est construite avec Django REST Framework (DRF), et sa version 1 est servie sous `/api/v1/`. Chaque app déclare
ses routes dans `api/urls.py`, sous son préfixe : `companies/`, `trips/`, `bookings/`, etc.

| Sujet | Règle commune (`REST_FRAMEWORK` dans `settings/base.py`) |
|---|---|
| Authentification | Jeton JWT dans l'en-tête `Authorization: Bearer <jeton>` |
| Accès | Connexion exigée par défaut, y compris pour un nouvel endpoint. Un endpoint public doit le déclarer avec `permission_classes = [AllowAny]` |
| Format | JSON uniquement |
| Pagination | 20 résultats par page sur les listes |
| Limitation | 60 requêtes par minute sans connexion, 300 avec, 10 pour les jetons |

| Méthode | Route | Corps | Réponse |
|---|---|---|---|
| POST | `/api/v1/auth/token/` | `email`, `password` | `access` (valable 30 minutes), `refresh` (valable 7 jours) |
| POST | `/api/v1/auth/token/refresh/` | `refresh` | Nouveau `access` |

En développement, ouvrir une route de l'API dans le navigateur affiche une interface de test.

La limitation s'appuie sur le cache de Django. En production avec plusieurs processus Gunicorn, il faudra un cache
partagé, par exemple Redis, pour que les compteurs soient communs. Les valeurs sont à ajuster pendant la phase pilote :
les utilisateurs d'un même opérateur mobile peuvent partager une adresse IP, et donc un même compteur.

L'API véhicules de `apps/companies/api/vehicles.py` date d'avant cette mise en place : elle n'utilise pas DRF et reste
sous `/compagnie/vehicules/api/`. Elle est à migrer vers `/api/v1/companies/`.

## Passer une page statique dans son app

Ces pages affichent encore leur maquette depuis `core/views.py`. Quand un domaine est développé, déplacer la vue et
la route dans son app, en gardant le nom `core:*` dans `core/urls.py` tant que les gabarits l'utilisent.

| Route actuelle | App cible |
|---|---|
| `core:compagnie_trajets` | `trips` |
| `core:compagnie_reservations`, `core:compagnie_regles` | `bookings` |
| `core:compagnie_dashboard`, `core:admin_dashboard` | `supervision` |
| `core:admin_utilisateurs`, `core:admin_reservations`, `core:admin_collecte` | `supervision` |

## Environnements

| Module de réglages | Usage | Sélection |
|---|---|---|
| `MutualTransport.settings.dev` | Développement local | Par défaut avec `manage.py` |
| `MutualTransport.settings.test` | Tests rapides | Option `--settings` |
| `MutualTransport.settings.staging` | Recette | Variable `DJANGO_SETTINGS_MODULE` |
| `MutualTransport.settings.prod` | Production | Par défaut avec `wsgi.py` et `asgi.py` |

`staging` et `prod` exigent ces variables d'environnement :

| Variable | Contenu |
|---|---|
| `DJANGO_SECRET_KEY` | Clé secrète, propre à chaque environnement |
| `DJANGO_ALLOWED_HOSTS` | Noms de domaine autorisés, séparés par des virgules |

La base de données de production reste à choisir : les réglages utilisent encore SQLite.

## Tests

```bash
python manage.py test --settings=MutualTransport.settings.test                 # tout le projet
python manage.py test apps.companies --settings=MutualTransport.settings.test  # une app
python manage.py makemigrations --check --dry-run                              # migrations à jour
```

## Travailler à plusieurs

- Créer une branche par fonctionnalité à partir de `main`.
- `db.sqlite3`, `media/` et les fichiers `.env` sont ignorés par git et ne doivent pas être versionnés.
- Avant de pousser, relancer les tests et vérifier les migrations.
- Si deux branches ajoutent une migration à la même app, supprimer la sienne et la regénérer après avoir récupéré
  celle de l'autre.

## Documentation des modules

- [Gestion des véhicules](docs/vehicles.md)
