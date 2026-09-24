from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import ConversationIA, MessageIA
from .ia_engine import repondre_chatbot

from produits.models import Produit, Categorie
from accounts.models import ProfilTransporteur
from commandes.models import Evaluation
from .ia_engine import (
    predire_revenus,
    suggerer_prix,
    analyser_sentiment,
    calculer_score_fiabilite_transporteur,
    prevoir_demande_categorie,
    detecter_agriculteurs_inactifs,
)


@login_required
def prediction_revenus(request):
    """Page principale de prédiction de revenus pour l'agriculteur."""
    if not request.user.est_agriculteur:
        from django.shortcuts import redirect
        return redirect('accueil')

    produits = request.user.profil_agriculteur.produits.filter(statut='actif')
    categories = Categorie.objects.all()

    resultat = None
    produit_selectionne = None

    if request.method == 'POST':
        produit_id = request.POST.get('produit_id')
        nb_mois = int(request.POST.get('nb_mois', 6))

        if produit_id:
            produit = get_object_or_404(Produit, pk=produit_id, agriculteur=request.user.profil_agriculteur)
            produit_selectionne = produit
            resultat = predire_revenus(
                prix_unitaire=produit.prix_unitaire,
                quantite_disponible=produit.quantite_disponible,
                produit_id=produit.pk,
                categorie_id=produit.categorie.pk if produit.categorie else None,
                nom_categorie=produit.categorie.nom if produit.categorie else None,
                nb_mois=nb_mois,
            )

    return render(request, 'assistant/prediction_revenus.html', {
        'produits': produits,
        'categories': categories,
        'resultat': resultat,
        'produit_selectionne': produit_selectionne,
    })


@login_required
def suggerer_prix_view(request):
    """Suggère un prix optimal pour un produit au moment de la publication."""
    if not request.user.est_agriculteur:
        return JsonResponse({'ok': False}, status=403)

    categorie_id = request.GET.get('categorie_id')
    est_bio = request.GET.get('est_bio') == '1'

    suggestion = suggerer_prix(
        nom_produit=request.GET.get('nom', ''),
        categorie_id=categorie_id,
        est_bio=est_bio,
    )

    return JsonResponse({'ok': True, 'suggestion': suggestion})


@login_required
def score_fiabilite_view(request, transporteur_id):
    """Page de score de fiabilité d'un transporteur."""
    profil = get_object_or_404(ProfilTransporteur, pk=transporteur_id)
    score_data = calculer_score_fiabilite_transporteur(profil)

    # Analyser le sentiment de ses évaluations
    evaluations = Evaluation.objects.filter(
        commande_livraison_transporteur=profil,
        cible='transporteur',
    ).exclude(commentaire='')[:20]

    sentiments = []
    for eval in evaluations:
        sentiment, score, mots = analyser_sentiment(eval.commentaire)
        sentiments.append({
            'commentaire': eval.commentaire,
            'note': eval.note,
            'sentiment': sentiment,
            'score': score,
        })

    score_data['evaluations_analysees'] = sentiments

    return render(request, 'assistant/score_fiabilite.html', {
        'profil': profil,
        'score_data': score_data,
    })


@login_required
def demande_categorie_view(request):
    """Prévision de la demande par catégorie — pour l'admin et les agriculteurs."""
    if not (request.user.est_agriculteur or request.user.est_admin):
        from django.shortcuts import redirect
        return redirect('accueil')

    categories = Categorie.objects.all()
    resultats = []

    categorie_id = request.GET.get('categorie_id')
    if categorie_id:
        predictions = prevoir_demande_categorie(categorie_id, nb_mois=4)
        categorie = get_object_or_404(Categorie, pk=categorie_id)
        resultats = predictions
    else:
        categorie = None

    return render(request, 'assistant/demande_categorie.html', {
        'categories': categories,
        'categorie': categorie,
        'resultats': resultats,
        'categorie_id': categorie_id,
    })


@login_required
def agriculteurs_inactifs_view(request):
    """Dashboard admin — agriculteurs inactifs."""
    if not request.user.est_admin:
        from django.shortcuts import redirect
        return redirect('accueil')

    jours = int(request.GET.get('jours', 30))
    inactifs = detecter_agriculteurs_inactifs(jours_seuil=jours)

    return render(request, 'assistant/agriculteurs_inactifs.html', {
        'inactifs': inactifs,
        'jours': jours,
        'nb_inactifs': len(inactifs),
    })
@login_required
def chat_widget_data(request):
    conversation, _ = ConversationIA.objects.get_or_create(utilisateur=request.user)
    messages = conversation.messages.all()
    return JsonResponse({
        'conversation_id': conversation.pk,
        'messages': [{'role': m.role, 'contenu': m.contenu} for m in messages],
    })


@login_required
@require_POST
def envoyer_message_chat(request):
    try:
        data = json.loads(request.body)
        texte = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'ok': False, 'erreur': 'Requête invalide.'}, status=400)

    if not texte:
        return JsonResponse({'ok': False, 'erreur': 'Message vide.'}, status=400)

    conversation, _ = ConversationIA.objects.get_or_create(utilisateur=request.user)

    derniers_messages = list(conversation.messages.order_by('-date_envoi')[:10])
    historique = [
        {'role': m.role, 'content': m.contenu}
        for m in reversed(derniers_messages)
    ]

    MessageIA.objects.create(conversation=conversation, role='user', contenu=texte)

    role_utilisateur = request.user.role if request.user.is_authenticated else None

    reponse_texte = repondre_chatbot(
        message=texte,
        historique=historique,
        role_utilisateur=role_utilisateur,
    )

    MessageIA.objects.create(conversation=conversation, role='assistant', contenu=reponse_texte)

    return JsonResponse({'ok': True, 'reponse': reponse_texte})



from accounts.models import ProfilAgriculteur
from livraisons.models import Livraison
from .geo_engine import (
    produits_proches,
    agriculteurs_proches,
    optimiser_itineraire,
    enrichir_produit_coords,
    enrichir_profil_agriculteur,
    geocoder_ville,
    distance_km,
)


# ============================================================
# CARTE CATALOGUE — Tous les produits géolocalisés
# ============================================================

def carte_catalogue(request):
    """Carte interactive de tous les produits disponibles."""
    produits = Produit.objects.filter(statut='actif').select_related(
        'agriculteur__utilisateur', 'categorie'
    ).prefetch_related('photos')

    # Géocoder automatiquement les produits sans coordonnées
    for p in produits:
        if not p.latitude:
            enrichir_produit_coords(p)

    categories = Categorie.objects.all()

    # Filtres
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        produits = produits.filter(categorie__id=categorie_id)

    # Préparer données JSON pour Leaflet
    markers = []
    for p in produits:
        if p.latitude and p.longitude:
            photo_url = ''
            premiere_photo = p.photos.first()
            if premiere_photo:
                photo_url = premiere_photo.image.url

            markers.append({
                'id': p.pk,
                'nom': p.nom,
                'prix': float(p.prix_unitaire),
                'unite': p.get_unite_display(),
                'est_bio': p.est_bio,
                'agriculteur': p.agriculteur.utilisateur.get_full_name(),
                'localisation': p.localisation or p.agriculteur.localisation or '',
                'lat': p.latitude,
                'lng': p.longitude,
                'url': f'/produits/produit/{p.pk}/',
                'photo': photo_url,
                'categorie': p.categorie.nom if p.categorie else '',
                'categorie_icone': p.categorie.icone if p.categorie else '🌿',
            })

    return render(request, 'assistant/carte_catalogue.html', {
        'markers_json': json.dumps(markers),
        'categories': categories,
        'nb_produits': len(markers),
        'categorie_id': categorie_id,
    })


# ============================================================
# CARTE AGRICULTEURS — Vue d'ensemble des producteurs
# ============================================================

def carte_agriculteurs(request):
    """Carte de tous les agriculteurs avec leurs produits."""
    agriculteurs = ProfilAgriculteur.objects.filter(
        produits__statut='actif'
    ).distinct().select_related('utilisateur').prefetch_related('produits')

    # Géocoder automatiquement
    for agri in agriculteurs:
        if not agri.latitude:
            enrichir_profil_agriculteur(agri)

    markers = []
    for agri in agriculteurs:
        if agri.latitude and agri.longitude:
            nb_produits = agri.produits.filter(statut='actif').count()
            markers.append({
                'id': agri.pk,
                'nom': agri.utilisateur.get_full_name(),
                'exploitation': agri.exploitation or '',
                'localisation': agri.localisation or '',
                'lat': agri.latitude,
                'lng': agri.longitude,
                'nb_produits': nb_produits,
                'note': float(agri.note_moyenne) if agri.note_moyenne else 0,
                'est_verifie': agri.est_verifie,
                'url': f'/produits/catalogue/?agriculteur={agri.pk}',
            })

    return render(request, 'assistant/carte_agriculteurs.html', {
        'markers_json': json.dumps(markers),
        'nb_agriculteurs': len(markers),
    })


# ============================================================
# MAJ POSITION — Endpoint AJAX pour GPS utilisateur
# ============================================================

@login_required
@require_POST
def maj_position_utilisateur(request):
    """Met à jour la position GPS de l'utilisateur connecté."""
    try:
        data = json.loads(request.body)
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'erreur': 'Coordonnées invalides.'}, status=400)

    user = request.user

    if user.est_agriculteur and hasattr(user, 'profil_agriculteur'):
        profil = user.profil_agriculteur
        profil.latitude = lat
        profil.longitude = lng
        profil.save(update_fields=['latitude', 'longitude'])

    elif user.est_acheteur and hasattr(user, 'profil_acheteur'):
        profil = user.profil_acheteur
        profil.latitude = lat
        profil.longitude = lng
        profil.save(update_fields=['latitude', 'longitude'])

    elif user.est_transporteur and hasattr(user, 'profil_transporteur'):
        profil = user.profil_transporteur
        profil.latitude_actuelle = lat
        profil.longitude_actuelle = lng
        profil.save(update_fields=['latitude_actuelle', 'longitude_actuelle'])

    return JsonResponse({'ok': True})


# ============================================================
# PRODUITS PROCHES — Pour l'acheteur
# ============================================================

@login_required
def produits_proches_view(request):
    """Liste des produits les plus proches de l'acheteur."""
    if not request.user.est_acheteur:
        from django.shortcuts import redirect
        return redirect('catalogue')

    profil = request.user.profil_acheteur
    rayon = int(request.GET.get('rayon', 50))

    if not profil.latitude:
        # Pas encore de position connue
        return render(request, 'assistant/produits_proches.html', {
            'resultats': [],
            'position_connue': False,
            'rayon': rayon,
        })

    produits = Produit.objects.filter(statut='actif').select_related(
        'agriculteur__utilisateur', 'categorie'
    ).prefetch_related('photos')

    for p in produits:
        if not p.latitude:
            enrichir_produit_coords(p)

    resultats = produits_proches(
        lat_acheteur=profil.latitude,
        lon_acheteur=profil.longitude,
        produits=produits,
        rayon_km=rayon,
    )

    # Préparer markers pour la carte
    markers = []
    for r in resultats:
        p = r['produit']
        if p.latitude and p.longitude:
            markers.append({
                'nom': p.nom,
                'prix': float(p.prix_unitaire),
                'unite': p.get_unite_display(),
                'lat': p.latitude,
                'lng': p.longitude,
                'distance': r['distance_km'],
                'url': f'/produits/produit/{p.pk}/',
            })

    return render(request, 'assistant/produits_proches.html', {
        'resultats': resultats[:20],
        'position_connue': True,
        'rayon': rayon,
        'lat_acheteur': profil.latitude,
        'lng_acheteur': profil.longitude,
        'markers_json': json.dumps(markers),
    })


# ============================================================
# ITINÉRAIRE OPTIMAL — Pour le transporteur
# ============================================================

@login_required
def itineraire_optimal_view(request):
    """Calcule l'itinéraire optimal pour le transporteur."""
    if not request.user.est_transporteur:
        from django.shortcuts import redirect
        return redirect('accueil')

    profil = request.user.profil_transporteur

    # Récupérer les livraisons en attente ou assignées
    livraisons = Livraison.objects.filter(
        transporteur=profil,
        statut__in=['assignee', 'en_route'],
    ).select_related(
        'commande__acheteur__utilisateur',
        'commande__agriculteur',
    )

    itineraire = None
    if livraisons.exists() and profil.latitude_actuelle:
        # Préparer les données
        points = []
        for liv in livraisons:
            commande = liv.commande
            points.append({
                'id': liv.pk,
                'commande_id': commande.pk,
                'acheteur_nom': commande.acheteur.utilisateur.get_full_name(),
                'adresse': commande.adresse_livraison,
                'lat_dest': commande.latitude_livraison,
                'lng_dest': commande.longitude_livraison,
                'montant': float(commande.montant_total),
            })

        position_depart = {
            'lat': profil.latitude_actuelle,
            'lng': profil.longitude_actuelle,
        }

        itineraire = optimiser_itineraire(position_depart, points)

        # Préparer les markers pour la carte
        markers = []
        for etape in itineraire['ordre']:
            if etape.get('lat_dest') and etape.get('lng_dest'):
                markers.append({
                    'ordre': etape['ordre_num'],
                    'nom': etape['acheteur_nom'],
                    'adresse': etape['adresse'],
                    'lat': etape['lat_dest'],
                    'lng': etape['lng_dest'],
                    'distance': etape['distance_km'],
                    'duree': etape['duree_minutes'],
                })

        itineraire['markers_json'] = json.dumps(markers)
        itineraire['depart_lat'] = profil.latitude_actuelle
        itineraire['depart_lng'] = profil.longitude_actuelle

    return render(request, 'assistant/itineraire_optimal.html', {
        'livraisons': livraisons,
        'itineraire': itineraire,
        'position_connue': bool(profil.latitude_actuelle),
        'profil': profil,
    })


# ============================================================
# GÉOCODER ADRESSE — Endpoint AJAX
# ============================================================

def geocoder_adresse(request):
    """Géocode une adresse camerounaise en coordonnées GPS."""
    adresse = request.GET.get('adresse', '')
    lat, lng = geocoder_ville(adresse)

    if lat:
        return JsonResponse({'ok': True, 'lat': lat, 'lng': lng})
    return JsonResponse({'ok': False, 'message': 'Ville non reconnue dans notre base de données.'})