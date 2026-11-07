from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_email_is_normalized_on_creation(self):
        user = User.objects.create_user(email='Contact@Nagode.TG', password='x')
        self.assertEqual(user.email, 'contact@nagode.tg')

    def test_username_is_the_email(self):
        self.assertEqual(User(email='a@b.tg').username, 'a@b.tg')

    def test_default_role_is_passenger(self):
        self.assertEqual(User.objects.create_user(email='a@b.tg').role, User.Role.PASSENGER)

    def test_superuser_is_admin(self):
        user = User.objects.create_superuser(email='admin@b.tg', password='x')
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff and user.is_superuser)

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')

    def test_email_uniqueness_ignores_case_in_database(self):
        User.objects.create(email='a@b.tg')
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create(email='A@B.tg')

    def test_email_uniqueness_ignores_case_in_validation(self):
        User.objects.create(email='a@b.tg')
        with self.assertRaises(ValidationError):
            User(email='A@B.tg', password='x').full_clean()
