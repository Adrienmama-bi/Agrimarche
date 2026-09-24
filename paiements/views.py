from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import random
from commandes.models import Commande
from .models import Paiement
from notifications.utils import notifier


@login_required
def payer_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)

    if commande.acheteur.utilisateur != request.user:
        messages.error(request, "Vous n'avez pas accès à cette commande.")
        return redirect('accueil')

    # Si un paiement existe déjà et est confirmé, on ne repasse pas par ici
    paiement_existant = Paiement.objects.filter(commande=commande).first()
    if paiement_existant and paiement_existant.statut == 'confirme':
        return redirect('detail_commande', pk=commande.pk)

    if request.method == 'POST':
        methode = request.POST.get('methode')
        numero = request.POST.get('numero', '')

        commission = round(float(commande.montant_total) * 0.03, 2)  # 3% de commission plateforme

        paiement, _ = Paiement.objects.update_or_create(
            commande=commande,
            defaults={
                'montant': commande.montant_total,
                'methode': methode,
                'statut': 'en_attente',
                'commission': commission,
                'reference_externe': f"AGM-{random.randint(100000, 999999)}",
            }
        )

        return redirect('confirmer_paiement', pk=paiement.pk)

    return render(request, 'paiements/payer.html', {
        'commande': commande,
    })


@login_required
def confirmer_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk, commande__acheteur__utilisateur=request.user)

    if request.method == 'POST':
        # Simulation de la passerelle de paiement (Mobile Money / Stripe)
        # En production, ceci serait remplacé par un appel API réel
        paiement.statut = 'confirme'
        paiement.save()

        commande = paiement.commande
        commande.statut = 'en_attente'  # reste en_attente jusqu'à validation par l'agriculteur
        commande.save()

        messages.success(request, "Paiement confirmé ! Votre commande a été transmise à l'agriculteur.")
        return redirect('recu_paiement', pk=paiement.pk)

    return render(request, 'paiements/confirmer.html', {'paiement': paiement})


@login_required
def recu_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)

    est_concerne = (
        (request.user.est_acheteur and paiement.commande.acheteur.utilisateur == request.user) or
        (request.user.est_agriculteur and paiement.commande.agriculteur.utilisateur == request.user)
    )
    if not est_concerne and not request.user.est_admin:
        return redirect('accueil')

    return render(request, 'paiements/recu.html', {'paiement': paiement})

@login_required
def mes_paiements(request):
    from django.db.models import Sum

    user = request.user

    if user.est_acheteur:
        paiements = Paiement.objects.filter(
            commande__acheteur=user.profil_acheteur
        ).select_related(
            'commande__acheteur__utilisateur',
            'commande__agriculteur__utilisateur',
        ).order_by('-date_transaction')

        stats = paiements.filter(statut='confirme').aggregate(
            total=Sum('montant'),
            total_commission=Sum('commission'),
        )
        total_montant = stats['total'] or 0
        total_commission = stats['total_commission'] or 0

    elif user.est_agriculteur:
        paiements = Paiement.objects.filter(
            commande__agriculteur=user.profil_agriculteur
        ).select_related(
            'commande__acheteur__utilisateur',
            'commande__agriculteur__utilisateur',
        ).order_by('-date_transaction')

        total_montant = paiements.filter(
            statut='confirme'
        ).aggregate(total=Sum('montant'))['total'] or 0
        total_commission = paiements.filter(
            statut='confirme'
        ).aggregate(total=Sum('commission'))['total'] or 0
        total_montant = float(total_montant) * 0.97  # Net après commission

    else:
        return redirect('dashboard')

    nb_confirmes = paiements.filter(statut='confirme').count()
    nb_attente = paiements.filter(statut='en_attente').count()

    return render(request, 'paiements/liste_paiements.html', {
        'paiements': paiements,
        'total_montant': round(float(total_montant)),
        'total_commission': round(float(total_commission)),
        'nb_confirmes': nb_confirmes,
        'nb_attente': nb_attente,
    })




