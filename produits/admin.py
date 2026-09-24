from django.contrib import admin
from .models import Produit, Categorie, PhotoProduit


class PhotoProduitInline(admin.TabularInline):
    model = PhotoProduit
    extra = 1


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'agriculteur', 'categorie', 'prix_unitaire', 'quantite_disponible', 'statut', 'est_bio', 'date_publication']
    list_filter = ['statut', 'categorie', 'est_bio']
    search_fields = ['nom', 'agriculteur_utilisateur_username']
    actions = ['valider_produits', 'suspendre_produits']
    inlines = [PhotoProduitInline]

    @admin.action(description="Valider les produits sélectionnés")
    def valider_produits(self, request, queryset):
        queryset.update(statut='actif')

    @admin.action(description="Suspendre les produits sélectionnés")
    def suspendre_produits(self, request, queryset):
        queryset.update(statut='suspendu')


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'icone', 'categorie_parente']