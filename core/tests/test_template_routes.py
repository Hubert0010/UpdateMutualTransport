"""Les gabarits sont gérés par le frontend : le backend doit fournir les routes qu'ils utilisent."""
import re

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse

URL_TAG = re.compile(r"""\{%\s*url\s+'([\w:]+)'((?:\s+[^%]+?)?)\s*%\}""")


class TemplateRoutesTests(SimpleTestCase):
    def test_every_route_used_by_the_templates_exists(self):
        templates = list(settings.BASE_DIR.glob('core/templates/**/*.html'))
        templates += list(settings.BASE_DIR.glob('apps/*/templates/**/*.html'))
        self.assertTrue(templates)

        routes = {
            (name, bool(args.strip()))
            for template in templates
            for name, args in URL_TAG.findall(template.read_text())
        }
        self.assertIn(('core:compagnie_profil', False), routes)
        for name, has_args in routes:
            with self.subTest(route=name):
                reverse(name, args=[1] if has_args else [])
