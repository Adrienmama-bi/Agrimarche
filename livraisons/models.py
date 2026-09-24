from django.db import models
from accounts.models import ProfilTransporteur, Vehicule
from commandes.models import Commande


class Livraison(models.Model):
    STATUT_CHOICES = [
        ('en_attente', "En attente d'un transporteur"), ('assignee', 'Assignée'),
        ('en_route', 'En route'), ('arrivee', 'Arrivée à destination'),
        ('livree', 'Livrée'), ('echec', 'Échec de livraison'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='livraison')
    transporteur = models.ForeignKey(ProfilTransporteur, on_delete=models.SET_NULL, null=True, blank=True, related_name='livraisons')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    point_depart_lat = models.FloatField(null=True, blank=True)
    point_depart_lng = models.FloatField(null=True, blank=True)
    point_arrivee_lat = models.FloatField(null=True, blank=True)
    point_arrivee_lng = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    tarif = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    eta = models.DateTimeField(null=True, blank=True)
    position_actuelle_lat = models.FloatField(null=True, blank=True)
    position_actuelle_lng = models.FloatField(null=True, blank=True)
    derniere_position_maj = models.DateTimeField(null=True, blank=True)
    preuve_livraison = models.ImageField(upload_to='preuves/', null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    

    def _str_(self):
        return f"Livraison #{self.pk} — {self.statut}"