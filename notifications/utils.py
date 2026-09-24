from .models import Notification


def notifier(destinataire, titre, contenu, type_notif='systeme', lien=''):
    """
    Crée une notification pour un utilisateur.
    Fonction centrale utilisée partout dans l'application.
    """
    return Notification.objects.create(
        destinataire=destinataire,
        titre=titre,
        contenu=contenu,
        type_notif=type_notif,
        lien=lien,
    )