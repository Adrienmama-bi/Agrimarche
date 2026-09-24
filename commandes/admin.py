from django.contrib import admin
from .models import Commande, LigneCommande, Evaluation


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ['sous_total']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'acheteur', 'agriculteur', 'montant_total', 'statut', 'date_commande']
    list_filter = ['statut', 'date_commande']
    search_fields = ['acheteur_utilisateurusername', 'agriculteurutilisateur_username']
    inlines = [LigneCommandeInline]


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['commande', 'note', 'cible', 'date_evaluation']
    list_filter = ['cible', 'note']