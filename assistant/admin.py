from django.contrib import admin
from .models import ConversationIA, MessageIA, RecommandationProduit


class MessageIAInline(admin.TabularInline):
    model = MessageIA
    extra = 0
    readonly_fields = ['date_envoi']


@admin.register(ConversationIA)
class ConversationIAAdmin(admin.ModelAdmin):
    list_display = ['pk', 'utilisateur', 'date_creation']
    inlines = [MessageIAInline]


@admin.register(RecommandationProduit)
class RecommandationProduitAdmin(admin.ModelAdmin):
    list_display = ['acheteur', 'produit', 'raison', 'ordre', 'date_calcul']
    list_filter = ['date_calcul']