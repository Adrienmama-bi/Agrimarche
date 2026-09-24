from django.db import models
from accounts.models import ProfilAcheteur, ProfilAgriculteur
from produits.models import Produit
from decimal import Decimal


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'), ('validee', 'Validée'),
        ('en_preparation', 'En préparation'), ('en_livraison', 'En livraison'),
        ('livree', 'Livrée'), ('annulee', 'Annulée'),
    ]

    acheteur = models.ForeignKey(ProfilAcheteur, on_delete=models.CASCADE, related_name='commandes')
    agriculteur = models.ForeignKey(ProfilAgriculteur, on_delete=models.CASCADE, related_name='commandes_recues')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adresse_livraison = models.CharField(max_length=300)
    latitude_livraison = models.FloatField(null=True, blank=True)
    longitude_livraison = models.FloatField(null=True, blank=True)
    date_livraison_souhaitee = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_commande']

    def _str_(self):
        return f"Commande #{self.pk}"

    def calculer_montant(self):
        total = sum(ligne.sous_total for ligne in self.lignes.all())
        self.montant_total = total
        self.save()
        return total


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.FloatField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.sous_total = self.prix_unitaire * Decimal(str(self.quantite))
        super().save(*args, **kwargs)


class Evaluation(models.Model):
    CIBLE_CHOICES = [('agriculteur', 'Agriculteur'), ('transporteur', 'Transporteur')]

    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='evaluations')
    note = models.IntegerField()
    commentaire = models.TextField(blank=True)
    cible = models.CharField(max_length=20, choices=CIBLE_CHOICES)
    date_evaluation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Évaluation'

    def _str_(self):
        return f"Note {self.note}/5 ({self.cible})"