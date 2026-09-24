from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, ProfilAgriculteur, ProfilAcheteur, ProfilTransporteur, Vehicule


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'statut', 'date_inscription']
    list_filter = ['role', 'statut']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations AgriMarché', {'fields': ('role', 'telephone', 'photo', 'statut')}),
    )


@admin.register(ProfilAgriculteur)
class ProfilAgriculteurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'exploitation', 'localisation', 'note_moyenne', 'est_verifie']
    list_filter = ['est_verifie']
    search_fields = ['utilisateur__username', 'exploitation']


@admin.register(ProfilAcheteur)
class ProfilAcheteurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type_acheteur', 'adresse_livraison']
    list_filter = ['type_acheteur']


@admin.register(ProfilTransporteur)
class ProfilTransporteurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'disponible', 'note_moyenne', 'est_verifie']
    list_filter = ['disponible', 'est_verifie']


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ['immatriculation', 'type_vehicule', 'transporteur', 'capacite_kg', 'est_actif']
    list_filter = ['type_vehicule', 'est_actif']