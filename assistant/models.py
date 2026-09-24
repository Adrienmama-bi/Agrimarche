from django.db import models
from accounts.models import Utilisateur, ProfilAcheteur
from produits.models import Produit


class ConversationIA(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='conversations_ia')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conversation IA'
        ordering = ['-date_creation']

    def _str_(self):
        return f"Conversation IA #{self.pk} — {self.utilisateur}"


class MessageIA(models.Model):
    ROLE_CHOICES = [('user', 'Utilisateur'), ('assistant', 'Assistant')]

    conversation = models.ForeignKey(ConversationIA, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_envoi']

    def _str_(self):
        return f"{self.role} : {self.contenu[:50]}"


class RecommandationProduit(models.Model):
    acheteur = models.ForeignKey(ProfilAcheteur, on_delete=models.CASCADE, related_name='recommandations')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    raison = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0)
    date_calcul = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recommandation produit'
        ordering = ['ordre']

    def _str_(self):
        return f"{self.produit.nom} → {self.acheteur}"