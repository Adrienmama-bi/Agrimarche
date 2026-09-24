from django import forms
from .models import Commande


class CommandeForm(forms.Form):
    quantite = forms.FloatField(min_value=0.5)
    adresse_livraison = forms.CharField(max_length=300)
    date_livraison_souhaitee = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    notes = forms.CharField(required=False, widget=forms.Textarea)