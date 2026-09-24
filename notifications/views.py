from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from notifications.utils import notifier


@login_required
def liste_notifications(request):
    notifications = Notification.objects.filter(destinataire=request.user)
    notifications.filter(est_lue=False).update(est_lue=True)
    return render(request, 'notifications/liste.html', {
        'notifications': notifications,
    })


@login_required
def aller_vers_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.est_lue = True
    notif.save()
    if notif.lien:
        return redirect(notif.lien)
    return redirect('liste_notifications')