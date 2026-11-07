"""Utilisateur de la plateforme : voyageur, compagnie ou administrateur."""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', self.model.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields['is_staff'] is not True or extra_fields['is_superuser'] is not True:
            raise ValueError('Un superutilisateur doit avoir is_staff=True et is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractUser):
    class Role(models.TextChoices):
        PASSENGER = 'passenger', 'Voyageur'
        COMPANY = 'company', 'Compagnie'
        ADMIN = 'admin', 'Administrateur'

    email = models.EmailField('adresse e-mail', unique=True)
    role = models.CharField('rôle', max_length=20, choices=Role.choices, default=Role.PASSENGER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'utilisateur'
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_user_email_case_insensitive',
                violation_error_message='Un compte utilise déjà cette adresse e-mail.',
            ),
        ]

    def __str__(self):
        return self.email

    @property
    def username(self):
        """Les gabarits existants affichent request.user.username."""
        return self.email
