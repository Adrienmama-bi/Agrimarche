from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Livraison
from notifications.utils import notifier


@login_required
def missions_disponibles(request):
    if not request.user.est_transporteur:
        return redirect('accueil')
    missions = Livraison.objects.filter(statut='en_attente').select_related(
        'commande__agriculteur__utilisateur', 'commande__acheteur__utilisateur'
    )
    return render(request, 'livraisons/missions_disponibles.html', {'missions': missions})


@login_required
def accepter_mission(request, pk):
    if not request.user.est_transporteur:
        return redirect('accueil')
    profil = request.user.profil_transporteur
    livraison = get_object_or_404(Livraison, pk=pk, statut='en_attente')

    if request.method == 'POST':
        vehicule_id = request.POST.get('vehicule')
        tarif = request.POST.get('tarif') or None
        distance_km = request.POST.get('distance_km') or None

        livraison.transporteur = profil
        if vehicule_id:
            from accounts.models import Vehicule
            livraison.vehicule = Vehicule.objects.filter(pk=vehicule_id, transporteur=profil).first()
        if tarif:
            livraison.tarif = tarif
        if distance_km:
            livraison.distance_km = distance_km
        livraison.statut = 'assignee'
        livraison.date_debut = timezone.now()
        livraison.save()

        commande = livraison.commande
        commande.statut = 'en_livraison'
        commande.save()

        notifier(
            destinataire=livraison.commande.acheteur.utilisateur,
            titre="Transporteur assigné",
            contenu=f"{profil.utilisateur.get_full_name()} a accepté de livrer votre commande #{livraison.commande.pk}.",
            type_notif='livraison',
            lien=f'/livraisons/{livraison.pk}/',
        )
        notifier(
            destinataire=livraison.commande.agriculteur.utilisateur,
            titre="Transporteur assigné",
            contenu=f"{profil.utilisateur.get_full_name()} va récupérer la commande #{livraison.commande.pk}.",
            type_notif='livraison',
            lien=f'/livraisons/{livraison.pk}/',
        )

        messages.success(request, f"Mission #{livraison.pk} acceptée ! Bonne route.")
        return redirect('mes_livraisons')

    vehicules = profil.vehicules.filter(est_actif=True)
    return render(request, 'livraisons/accepter_mission.html', {
        'livraison': livraison,
        'vehicules': vehicules,
    })


@login_required
def mes_livraisons(request):
    if not request.user.est_transporteur:
        return redirect('accueil')
    profil = request.user.profil_transporteur
    livraisons = profil.livraisons.all().select_related(
        'commande__agriculteur__utilisateur', 'commande__acheteur__utilisateur'
    )
    return render(request, 'livraisons/mes_livraisons.html', {'livraisons': livraisons})


@login_required
def detail_livraison(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)

    est_transporteur_concerne = (
        request.user.est_transporteur and
        livraison.transporteur and
        livraison.transporteur.utilisateur == request.user
    )
    est_acheteur_concerne = (
        request.user.est_acheteur and
        livraison.commande.acheteur.utilisateur == request.user
    )
    est_agriculteur_concerne = (
        request.user.est_agriculteur and
        livraison.commande.agriculteur.utilisateur == request.user
    )

    if not (est_transporteur_concerne or est_acheteur_concerne or est_agriculteur_concerne or request.user.est_admin):
        messages.error(request, "Vous n'avez pas accès à cette livraison.")
        return redirect('accueil')

    return render(request, 'livraisons/detail_livraison.html', {
        'livraison': livraison,
        'est_transporteur_concerne': est_transporteur_concerne,
    })


@login_required
def mettre_a_jour_statut(request, pk, nouveau_statut):
    if not request.user.est_transporteur:
        return redirect('accueil')
    livraison = get_object_or_404(
        Livraison, pk=pk, transporteur=request.user.profil_transporteur
    )

    statuts_valides = ['en_route', 'arrivee', 'livree']
    if nouveau_statut not in statuts_valides:
        return redirect('detail_livraison', pk=pk)

    if request.method == 'POST':
        livraison.statut = nouveau_statut

        if nouveau_statut == 'livree':
            livraison.date_fin = timezone.now()
            preuve = request.FILES.get('preuve')
            if preuve:
                livraison.preuve_livraison = preuve
            livraison.commande.statut = 'livree'
            livraison.commande.save()

            # Mise à jour des revenus du transporteur
            if livraison.tarif:
                profil = livraison.transporteur
                profil.revenus_total += livraison.tarif
                profil.save()

        libelles = {
            'en_route': 'est en route vers vous',
            'arrivee': 'est arrivé à destination',
            'livree': 'a été livrée',
        }
        notifier(
            destinataire=livraison.commande.acheteur.utilisateur,
            titre="Mise à jour de livraison",
            contenu=f"Votre commande #{livraison.commande.pk} {libelles.get(nouveau_statut, 'a été mise à jour')}.",
            type_notif='livraison',
            lien=f'/livraisons/{livraison.pk}/',
        )

        livraison.save()
        messages.success(request, "Statut mis à jour.")
        return redirect('detail_livraison', pk=pk)

    return render(request, 'livraisons/confirmer_statut.html', {
        'livraison': livraison,
        'nouveau_statut': nouveau_statut,
    })
    from django.http import JsonResponse
from django.utils import timezone


@login_required
def mettre_a_jour_position(request, pk):
    """Reçoit la position GPS du transporteur (appelé en AJAX depuis le navigateur)."""
    if not request.user.est_transporteur:
        return JsonResponse({'ok': False}, status=403)

    livraison = get_object_or_404(Livraison, pk=pk, transporteur=request.user.profil_transporteur)

    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if lat and lng:
            livraison.position_actuelle_lat = float(lat)
            livraison.position_actuelle_lng = float(lng)
            livraison.derniere_position_maj = timezone.now()
            livraison.save(update_fields=['position_actuelle_lat', 'position_actuelle_lng', 'derniere_position_maj'])
            return JsonResponse({'ok': True})

    return JsonResponse({'ok': False}, status=400)


@login_required
def position_livraison(request, pk):
    """Renvoie la position actuelle en JSON (appelé en polling par l'acheteur/agriculteur)."""
    livraison = get_object_or_404(Livraison, pk=pk)

    est_concerne = (
        (request.user.est_transporteur and livraison.transporteur and livraison.transporteur.utilisateur == request.user) or
        (request.user.est_acheteur and livraison.commande.acheteur.utilisateur == request.user) or
        (request.user.est_agriculteur and livraison.commande.agriculteur.utilisateur == request.user)
    )
    if not est_concerne:
        return JsonResponse({'ok': False}, status=403)

    return JsonResponse({
        'ok': True,
        'lat': livraison.position_actuelle_lat,
        'lng': livraison.position_actuelle_lng,
        'statut': livraison.statut,
        'statut_display': livraison.get_statut_display(),
        'derniere_maj': livraison.derniere_position_maj.strftime('%H:%M:%S') if livraison.derniere_position_maj else None,
    })