from django import forms
from ..models import Vehicle

class VehicleForm(forms.ModelForm):
    def __init__(self, *args, company=None, **kwargs):
        self.company = company
        super().__init__(*args, **kwargs)

    class Meta:
        model = Vehicle
        exclude = ("company", "created_at", "updated_at")
        widgets = {
            "technical_inspection_expiry": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "registration_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "TG-1234-BR"}),
            "brand_model": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex. Scania Touring"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "seats": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 100}),
            "insurance_policy_number": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "registration_number": "Immatriculation",
            "brand_model": "Marque et modèle",
            "category": "Catégorie",
            "seats": "Nombre de places",
            "has_ac": "Climatisation",
            "has_wifi": "Wi-Fi",
            "has_usb": "Prises USB",
            "technical_inspection_expiry": "Expiration de la visite technique",
            "insurance_policy_number": "Numéro de police d'assurance",
            "status": "Statut",
            "notes": "Observations",
        }

    def clean_registration_number(self):
        plate = self.cleaned_data["registration_number"].strip().upper().replace(" ", "")
        if self.company:
            duplicate = Vehicle.objects.filter(company=self.company, registration_number=plate)
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError("Cette immatriculation existe déjà dans votre flotte.")
        return plate
