from django.utils import timezone
from .ia_engine import analyser_produit_local


def analyser_produit(produit):
    """Analyse un produit avec notre moteur local et sauvegarde le résultat."""
    statut, raison = analyser_produit_local(produit)

    produit.statut_ia = statut
    produit.raison_ia = raison
    produit.date_analyse_ia = timezone.now()
    produit.save(update_fields=['statut_ia', 'raison_ia', 'date_analyse_ia'])

    return statut, raison