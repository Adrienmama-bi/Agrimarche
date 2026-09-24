from django.db import models
from accounts.models import Utilisateur


class Conversation(models.Model):
    participants = models.ManyToManyField(Utilisateur, related_name='conversations')
    date_creation = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    TYPE_CHOICES = [('texte', 'Texte'), ('image', 'Image'), ('fichier', 'Fichier')]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)
    piece_jointe = models.FileField(upload_to='messagerie/', null=True, blank=True)
    type_message = models.CharField(max_length=10, choices=TYPE_CHOICES, default='texte')

    class Meta:
        ordering = ['date_envoi']