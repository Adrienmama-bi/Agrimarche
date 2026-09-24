from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, ProfilAgriculteur, ProfilAcheteur, ProfilTransporteur, Vehicule




class InscriptionForm(UserCreationForm):
    role = forms.ChoiceField(choices=Utilisateur.ROLE_CHOICES, widget=forms.HiddenInput())
    telephone = forms.CharField(max_length=20, required=True)

    # Champs spécifiques selon le rôle
    exploitation = forms.CharField(max_length=200, required=False)
    localisation = forms.CharField(max_length=200, required=False)
    adresse_livraison = forms.CharField(max_length=300, required=False)

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('username', 'first_name', 'last_name', 'email', 'telephone', 'role')

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        if role == 'agriculteur' and not cleaned.get('exploitation'):
            self.add_error('exploitation', "Indiquez le nom de votre exploitation.")
        if role == 'acheteur' and not cleaned.get('adresse_livraison'):
            self.add_error('adresse_livraison', "Indiquez votre adresse de livraison.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.telephone = self.cleaned_data['telephone']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            role = user.role
            if role == 'agriculteur':
                ProfilAgriculteur.objects.create(
                    utilisateur=user,
                    exploitation=self.cleaned_data.get('exploitation', ''),
                    localisation=self.cleaned_data.get('localisation', ''),
                )
            elif role == 'acheteur':
                ProfilAcheteur.objects.create(
                    utilisateur=user,
                    adresse_livraison=self.cleaned_data.get('adresse_livraison', ''),
                )
            elif role == 'transporteur':
                ProfilTransporteur.objects.create(utilisateur=user)
        return user
class ProfilAgriculteurForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    telephone = forms.CharField(max_length=20)
    photo = forms.ImageField(required=False)

    class Meta:
        model = ProfilAgriculteur
        fields = ['exploitation', 'localisation', 'superficie', 'types_production', 'bio']


class ProfilAcheteurForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    telephone = forms.CharField(max_length=20)
    photo = forms.ImageField(required=False)

    class Meta:
        model = ProfilAcheteur
        fields = ['adresse_livraison', 'type_acheteur']


class ProfilTransporteurForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    telephone = forms.CharField(max_length=20)
    photo = forms.ImageField(required=False)

    class Meta:
        model = ProfilTransporteur
        fields = ['zone_couverture', 'disponible', 'numero_permis']


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['type_vehicule', 'immatriculation', 'capacite_kg', 'est_refrigere', 'annee', 'photo']