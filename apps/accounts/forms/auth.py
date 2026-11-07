"""Formulaire de connexion."""
from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    email = forms.EmailField(label='Adresse e-mail')
    password = forms.CharField(label='Mot de passe', strip=False, widget=forms.PasswordInput)
    remember = forms.BooleanField(label='Se souvenir de moi', required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Adresse e-mail ou mot de passe incorrect.')
        return cleaned_data
