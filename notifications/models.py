from django.db import models
from accounts.models import Utilisateur


class Notification(models.Model):
    TYPE_CHOICES = [
        ('commande', 'Commande'), ('paiement', 'Paiement'),
        ('livraison', 'Livraison'), ('message', 'Message'), ('systeme', 'Système'),
    ]
    CANAL_CHOICES = [('push', 'Push'), ('email', 'Email'), ('sms', 'SMS')]

    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    type_notif = models.CharField(max_length=20, choices=TYPE_CHOICES)
    canal = models.CharField(max_length=10, choices=CANAL_CHOICES, default='push')
    est_lue = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    lien = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date_envoi']
        