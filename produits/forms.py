from django import forms
from .models import Produit, PhotoProduit, Categorie


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'nom', 'categorie', 'description', 'prix_unitaire',
            'unite', 'quantite_disponible', 'quantite_min_commande',
            'date_recolte', 'date_expiration', 'est_bio',
            'localisation',
        ]
        widgets = {
            'date_recolte': forms.DateInput(attrs={'type': 'date'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['categorie'].queryset = Categorie.objects.all()
        self.fields['categorie'].empty_label = "Choisir une catégorie"