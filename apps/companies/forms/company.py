"""Formulaires de création et de modification d'une compagnie."""
from django import forms
from django.core.files.uploadedfile import UploadedFile

from apps.accounts.services.users import email_is_taken

from ..models import Company

LOGO_MAX_SIZE = 2 * 1024 * 1024  # 2 Mo


class CompanyCreateForm(forms.ModelForm):
    """Saisie de l'administrateur à la création d'un compte compagnie."""

    email = forms.EmailField(label='E-mail de connexion')

    class Meta:
        model = Company
        fields = [
            'legal_name', 'trade_name', 'manager_name',
            'rccm', 'nif', 'license_number',
            'city', 'region', 'address',
            'support_phone', 'contact_email',
        ]

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if email_is_taken(email):
            raise forms.ValidationError('Un compte utilise déjà cette adresse e-mail.')
        return email


class CompanyProfileForm(forms.ModelForm):
    """Informations modifiables par la compagnie depuis son profil."""

    class Meta:
        model = Company
        fields = [
            'legal_name', 'trade_name', 'manager_name',
            'support_phone', 'mobile_phone', 'contact_email',
            'address', 'description', 'logo',
            'tmoney_account', 'flooz_account', 'rib',
        ]

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if isinstance(logo, UploadedFile) and logo.size > LOGO_MAX_SIZE:
            raise forms.ValidationError('Le logo ne doit pas dépasser 2 Mo.')
        return logo
