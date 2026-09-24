from django.utils import timezone
from datetime import timedelta

from produits.models import Produit
from .models import RecommandationProduit
from .ia_engine import calculer_recommandations


def get_recommandations(acheteur, forcer_recalcul=False, limite=6):
    """Renvoie les recommandations en cache si récentes (<12h), sinon recalcule."""
    derniere = RecommandationProduit.objects.filter(acheteur=acheteur).order_by('-date_calcul').first()
    est_perime = (not derniere) or (timezone.now() - derniere.date_calcul > timedelta(hours=12))

    if forcer_recalcul or est_perime:
        produits_dispo = Produit.objects.filter(statut='actif').select_related(
            'categorie', 'agriculteur__utilisateur'
        ).prefetch_related('photos')

        resultats = calculer_recommandations(acheteur, produits_dispo, limite)

        RecommandationProduit.objects.filter(acheteur=acheteur).delete()
        for ordre, (produit, raison) in enumerate(resultats):
            RecommandationProduit.objects.create(
                acheteur=acheteur,
                produit=produit,
                raison=raison,
                ordre=ordre,
            )
        return resultats

    recos = RecommandationProduit.objects.filter(acheteur=acheteur).select_related(
        'produit__categorie', 'produit__agriculteur__utilisateur'
    ).prefetch_related('produit__photos')
    return [(r.produit, r.raison) for r in recos]