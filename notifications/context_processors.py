from .models import Notification


def notifications_non_lues(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(destinataire=request.user, est_lue=False).count()
        return {'nb_notifications_non_lues': count}
    return {'nb_notifications_non_lues': 0}