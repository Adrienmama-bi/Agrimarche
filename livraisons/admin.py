from django.contrib import admin
from .models import Livraison


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'commande', 'transporteur', 'statut', 'tarif', 'distance_km', 'date_creation']
    list_filter = ['statut']
    search_fields = ['transporteur_utilisateur_username']