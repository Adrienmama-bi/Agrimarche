from django.db import models
from commandes.models import Commande


class Paiement(models.Model):
    METHODE_CHOICES = [
        ('mobile_money', 'Mobile Money'), ('carte', 'Carte bancaire'),
        ('virement', 'Virement bancaire'), ('especes', 'Espèces à la livraison'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'), ('confirme', 'Confirmé'),
        ('rejete', 'Rejeté'), ('rembourse', 'Remboursé'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    devise = models.CharField(max_length=10, default='CDF')
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_transaction = models.DateTimeField(auto_now_add=True)
    reference_externe = models.CharField(max_length=100, blank=True)
    commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def _str_(self):
        return f"Paiement #{self.pk} — {self.montant} {self.devise}"