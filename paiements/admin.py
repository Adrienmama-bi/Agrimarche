from django.contrib import admin
from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['pk', 'commande', 'montant', 'devise', 'methode', 'statut', 'date_transaction']
    list_filter = ['methode', 'statut']
    search_fields = ['reference_externe']