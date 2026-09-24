from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from produits.models import Produit
from .models import Commande, LigneCommande
from notifications.utils import notifier
from django.db.models import Avg
from .models import Evaluation


@login_required
def passer_commande(request, produit_id):
    if not request.user.est_acheteur:
        messages.error(request, "Seuls les acheteurs peuvent passer commande.")
        return redirect('accueil')

    produit = get_object_or_404(Produit, pk=produit_id, statut='actif')
    profil = request.user.profil_acheteur

    if request.method == 'POST':
        quantite = float(request.POST.get('quantite', 0))
        adresse = request.POST.get('adresse', '')
        date_livraison = request.POST.get('date_livraison') or None
        notes = request.POST.get('notes', '')

        if quantite < produit.quantite_min_commande:
            messages.error(request, f"La quantité minimum est de {produit.quantite_min_commande} {produit.get_unite_display()}.")
            return redirect('detail_produit', pk=produit.pk)

        if quantite > produit.quantite_disponible:
            messages.error(request, "Quantité demandée supérieure au stock disponible.")
            return redirect('detail_produit', pk=produit.pk)

        # Création de la commande
        commande = Commande.objects.create(
            acheteur=profil,
            agriculteur=produit.agriculteur,
            adresse_livraison=adresse,
            date_livraison_souhaitee=date_livraison,
            notes=notes,
            statut='en_attente',
        )

        LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            quantite=quantite,
            prix_unitaire=produit.prix_unitaire,
        )

        commande.calculer_montant()

        # Mise à jour du stock
        produit.quantite_disponible -= quantite
        if produit.quantite_disponible <= 0:
            produit.statut = 'vendu'
        produit.save()

        messages.success(request, "Commande créée. Finalisez le paiement pour la confirmer.")
        return redirect('payer_commande', commande_id=commande.pk)

    return redirect('detail_produit', pk=produit.pk)


@login_required
def mes_commandes(request):
    if not request.user.est_acheteur:
        return redirect('accueil')
    profil = request.user.profil_acheteur
    commandes = profil.commandes.all().prefetch_related('lignes__produit')
    return render(request, 'commandes/mes_commandes.html', {'commandes': commandes})


@login_required
def detail_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    # Vérifier que l'utilisateur a le droit de voir cette commande
    est_acheteur_concerne = request.user.est_acheteur and commande.acheteur.utilisateur == request.user
    est_agriculteur_concerne = request.user.est_agriculteur and commande.agriculteur.utilisateur == request.user

    if not (est_acheteur_concerne or est_agriculteur_concerne or request.user.est_admin):
        messages.error(request, "Vous n'avez pas accès à cette commande.")
        return redirect('accueil')

    return render(request, 'commandes/detail_commande.html', {
        'commande': commande,
        'est_agriculteur_concerne': est_agriculteur_concerne,
    })


@login_required
def commandes_recues(request):
    if not request.user.est_agriculteur:
        return redirect('accueil')
    profil = request.user.profil_agriculteur
    commandes = profil.commandes_recues.all().prefetch_related('lignes__produit')
    return render(request, 'commandes/commandes_recues.html', {'commandes': commandes})


@login_required
def valider_commande(request, pk):
    if not request.user.est_agriculteur:
        return redirect('accueil')
    commande = get_object_or_404(Commande, pk=pk, agriculteur=request.user.profil_agriculteur)
    commande.statut = 'validee'
    commande.save()

    from livraisons.models import Livraison
    Livraison.objects.get_or_create(
        commande=commande,
        defaults={
            'point_depart_lat': commande.agriculteur.latitude,
            'point_depart_lng': commande.agriculteur.longitude,
            'point_arrivee_lat': commande.latitude_livraison,
            'point_arrivee_lng': commande.longitude_livraison,
            'statut': 'en_attente',
        }
    )

    notifier(
        destinataire=commande.acheteur.utilisateur,
        titre="Commande validée",
        contenu=f"{commande.agriculteur.utilisateur.get_full_name()} a validé votre commande #{commande.pk}.",
        type_notif='commande',
        lien=f'/commandes/{commande.pk}/',
    )

    messages.success(request, f"Commande #{commande.pk} validée. Une mission de livraison a été créée.")
    return redirect('detail_commande', pk=commande.pk)
@login_required
def refuser_commande(request, pk):
    if not request.user.est_agriculteur:
        return redirect('accueil')
    commande = get_object_or_404(Commande, pk=pk, agriculteur=request.user.profil_agriculteur)

    for ligne in commande.lignes.all():
        ligne.produit.quantite_disponible += ligne.quantite
        if ligne.produit.statut == 'vendu':
            ligne.produit.statut = 'actif'
        ligne.produit.save()

    commande.statut = 'annulee'
    commande.save()

    notifier(
        destinataire=commande.acheteur.utilisateur,
        titre="Commande refusée",
        contenu=f"Votre commande #{commande.pk} a été refusée par l'agriculteur.",
        type_notif='commande',
        lien=f'/commandes/{commande.pk}/',
    )

    messages.success(request, f"Commande #{commande.pk} refusée.")
    return redirect('commandes_recues')


@login_required
def evaluer_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk, acheteur=request.user.profil_acheteur)

    if commande.statut != 'livree':
        messages.error(request, "Vous ne pouvez évaluer qu'une commande déjà livrée.")
        return redirect('detail_commande', pk=pk)

    deja_evalue = commande.evaluations.exists()
    if deja_evalue:
        messages.info(request, "Vous avez déjà évalué cette commande.")
        return redirect('detail_commande', pk=pk)

    a_transporteur = hasattr(commande, 'livraison') and commande.livraison.transporteur is not None

    if request.method == 'POST':
        note_agri = request.POST.get('note_agriculteur')
        commentaire_agri = request.POST.get('commentaire_agriculteur', '')

        if note_agri:
            Evaluation.objects.create(
                commande=commande,
                note=int(note_agri),
                commentaire=commentaire_agri,
                cible='agriculteur',
            )
            agri_profil = commande.agriculteur
            moyenne = Evaluation.objects.filter(
                commande__agriculteur=agri_profil, cible='agriculteur'
            ).aggregate(Avg('note'))['note__avg']
            agri_profil.note_moyenne = round(moyenne, 1)
            agri_profil.save()

        if a_transporteur:
            note_trans = request.POST.get('note_transporteur')
            commentaire_trans = request.POST.get('commentaire_transporteur', '')
            if note_trans:
                Evaluation.objects.create(
                    commande=commande,
                    note=int(note_trans),
                    commentaire=commentaire_trans,
                    cible='transporteur',
                )
                trans_profil = commande.livraison.transporteur
                moyenne = Evaluation.objects.filter(
                    commande__livraison__transporteur=trans_profil, cible='transporteur'
                ).aggregate(Avg('note'))['note__avg']
                trans_profil.note_moyenne = round(moyenne, 1)
                trans_profil.save()

        messages.success(request, "Merci pour votre évaluation !")
        return redirect('detail_commande', pk=pk)

    return render(request, 'commandes/evaluer.html', {
        'commande': commande,
        'a_transporteur': a_transporteur,
    })


@login_required
def mes_avis(request):
    if request.user.est_agriculteur:
        profil = request.user.profil_agriculteur
        avis = Evaluation.objects.filter(
            commande__agriculteur=profil, cible='agriculteur'
        ).select_related('commande__acheteur__utilisateur').order_by('-date_evaluation')
    elif request.user.est_transporteur:
        profil = request.user.profil_transporteur
        avis = Evaluation.objects.filter(
            commande__livraison__transporteur=profil, cible='transporteur'
        ).select_related('commande__acheteur__utilisateur').order_by('-date_evaluation')
    else:
        return redirect('accueil')

    return render(request, 'commandes/mes_avis.html', {
        'avis': avis,
        'profil': profil,
    })