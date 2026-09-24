"""
Moteur IA local AgriMarché
Aucune dépendance externe — 100% Python standard
"""

import re
from collections import Counter


# ============================================================
# CHATBOT — Moteur à base de règles et mots-clés
# ============================================================

REPONSES_CHATBOT = {
    'inscription': {
        'mots_cles': ['inscrire', 'inscription', 'créer compte', 'créer un compte', 'rejoindre', 'comment je fais', 'comment créer', 'nouveau'],
        'reponse': "Pour vous inscrire sur AgriMarché, cliquez sur 'Créer un compte' en haut à droite, choisissez votre rôle (agriculteur, acheteur ou transporteur), remplissez le formulaire et c'est parti ! L'inscription est gratuite et prend moins de 2 minutes."
    },
    'connexion': {
        'mots_cles': ['connecter', 'connexion', 'login', 'mot de passe', 'identifiant', 'se connecter'],
        'reponse': "Pour vous connecter, cliquez sur 'Connexion' en haut à droite et entrez votre nom d'utilisateur et mot de passe. Si vous avez oublié votre mot de passe, utilisez le lien 'Mot de passe oublié' sur la page de connexion."
    },
    'publier_produit': {
        'mots_cles': ['publier', 'annonce', 'vendre', 'mettre en vente', 'ajouter produit', 'nouveau produit', 'comment vendre'],
        'reponse': "Pour publier un produit, connectez-vous en tant qu'agriculteur, allez dans votre tableau de bord → 'Publier un produit'. Remplissez le nom, la description, le prix, la quantité et ajoutez des photos. Votre annonce sera visible après validation par notre équipe."
    },
    'commande': {
        'mots_cles': ['commander', 'commande', 'acheter', 'passer commande', 'comment acheter', 'comment commander'],
        'reponse': "Pour passer une commande, allez dans le Catalogue, trouvez le produit qui vous intéresse, cliquez sur 'Voir' puis remplissez le formulaire de commande avec la quantité et votre adresse. Vous serez ensuite redirigé vers le paiement."
    },
    'paiement': {
        'mots_cles': ['payer', 'paiement', 'mobile money', 'carte', 'espèces', 'comment payer', 'moyen de paiement'],
        'reponse': "AgriMarché accepte trois méthodes de paiement : Mobile Money (M-Pesa, Airtel Money, Orange Money), carte bancaire (Visa, Mastercard), et espèces à la livraison. Choisissez votre méthode préférée lors de la commande."
    },
    'livraison': {
        'mots_cles': ['livraison', 'livrer', 'transport', 'transporteur', 'suivi', 'suivre', 'où est', 'ma commande', 'délai'],
        'reponse': "Une fois votre commande validée par l'agriculteur, un transporteur l'accepte et la livre à votre adresse. Vous pouvez suivre votre livraison en temps réel sur la carte depuis votre tableau de bord → 'Mes commandes'."
    },
    'statut_commande': {
        'mots_cles': ['statut', 'état', 'en attente', 'validée', 'annulée', 'refusée', 'progression'],
        'reponse': "Votre commande passe par ces étapes : En attente → Validée par l'agriculteur → En livraison → Livrée. Consultez le détail de votre commande depuis 'Mes commandes' pour voir l'étape actuelle."
    },
    'agriculteur_revenu': {
        'mots_cles': ['revenu', 'argent', 'gagner', 'combien', 'salaire', 'commission', 'paiement reçu', 'encaissement'],
        'reponse': "En tant qu'agriculteur, vous recevez le montant de vos ventes directement. AgriMarché prélève une commission de 3% sur chaque transaction pour couvrir les frais de plateforme. Vos revenus sont visibles dans votre tableau de bord."
    },
    'transporteur_mission': {
        'mots_cles': ['mission', 'missions', 'livraison disponible', 'accepter mission', 'comment transporter', 'trouver mission'],
        'reponse': "Pour trouver des missions, connectez-vous en tant que transporteur et allez dans 'Missions disponibles'. Vous verrez toutes les livraisons en attente près de vous. Cliquez sur 'Accepter' pour prendre une mission."
    },
    'note_evaluation': {
        'mots_cles': ['noter', 'évaluer', 'avis', 'note', 'commentaire', 'satisfaction'],
        'reponse': "Après chaque livraison, vous pouvez évaluer l'agriculteur et le transporteur avec une note de 1 à 5 étoiles et un commentaire. Allez dans 'Mes commandes', ouvrez la commande livrée et cliquez sur 'Évaluer'."
    },
    'profil': {
        'mots_cles': ['profil', 'modifier', 'changer', 'photo', 'informations personnelles', 'mettre à jour', 'modifier profil'],
        'reponse': "Pour modifier votre profil, allez dans votre tableau de bord → 'Mon profil'. Vous pouvez y changer votre photo, votre téléphone et toutes vos informations personnelles."
    },
    'support': {
        'mots_cles': ['aide', 'support', 'contact', 'problème', 'bug', 'erreur', 'signaler', 'contacter'],
        'reponse': "Pour tout problème, vous pouvez utiliser la messagerie interne pour contacter directement un agriculteur ou transporteur. Pour un problème technique, contactez notre équipe via la page Contact."
    },
    'salutation': {
        'mots_cles': ['bonjour', 'bonsoir', 'salut', 'hello', 'hey', 'coucou', 'bonne journée', 'bonne nuit'],
        'reponse': "Bonjour ! Je suis l'assistant d'AgriMarché 🌿 Je suis là pour répondre à toutes vos questions sur la plateforme. Comment puis-je vous aider aujourd'hui ?"
    },
    'merci': {
        'mots_cles': ['merci', 'thanks', 'thank you', 'parfait', 'super', 'excellent', 'très bien', 'ok merci'],
        'reponse': "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. Bonne expérience sur AgriMarché 🌿"
    },
    'catalogue': {
        'mots_cles': ['catalogue', 'produits', 'voir produits', 'trouver produit', 'chercher', 'recherche', 'filtrer'],
        'reponse': "Le catalogue est accessible depuis le menu 'Catalogue'. Vous pouvez filtrer par catégorie (céréales, légumes, fruits...), par prix, par localisation et par type bio ou non. Utilisez la barre de recherche pour un produit précis."
    },
    'vehicule': {
        'mots_cles': ['véhicule', 'voiture', 'camion', 'moto', 'ajouter véhicule', 'enregistrer véhicule'],
        'reponse': "En tant que transporteur, ajoutez votre véhicule depuis votre tableau de bord → 'Mon véhicule' → 'Ajouter un véhicule'. Précisez le type, l'immatriculation et la capacité. Cela vous permettra de l'utiliser lors de vos missions."
    },
}

REPONSE_PAR_DEFAUT = "Je n'ai pas bien compris votre question. Pouvez-vous reformuler ? Je peux vous aider sur : l'inscription, les commandes, les paiements, les livraisons, la publication de produits, ou tout autre sujet lié à AgriMarché."


def _normaliser(texte):
    """Supprime accents, ponctuation, met en minuscules."""
    texte = texte.lower().strip()
    remplacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ç': 'c', "'" : ' ', "'" : ' ',
    }
    for src, dst in remplacements.items():
        texte = texte.replace(src, dst)
    texte = re.sub(r'[^\w\s]', ' ', texte)
    return texte


def repondre_chatbot(message, historique=None, role_utilisateur=None):
    """
    Répond à un message utilisateur.
    historique : liste de dicts [{'role': 'user'/'assistant', 'content': '...'}, ...]
    role_utilisateur : 'agriculteur', 'acheteur', 'transporteur', 'admin' ou None
    """
    message_normalise = _normaliser(message)
    mots_message = set(message_normalise.split())

    meilleur_score = 0
    meilleure_reponse = None

    for categorie, data in REPONSES_CHATBOT.items():
        score = 0
        for mot_cle in data['mots_cles']:
            mot_cle_normalise = _normaliser(mot_cle)
            if mot_cle_normalise in message_normalise:
                # Phrase exacte trouvée
                score += len(mot_cle.split()) * 2
            else:
                # Mots individuels
                mots_cle = set(mot_cle_normalise.split())
                correspondances = mots_message & mots_cle
                score += len(correspondances)

        if score > meilleur_score:
            meilleur_score = score
            meilleure_reponse = data['reponse']

    # Personnalisation selon le rôle
    if meilleur_score == 0:
        reponse = REPONSE_PAR_DEFAUT
    else:
        reponse = meilleure_reponse

    # Ajout d'un contexte selon le rôle si pertinent
    if role_utilisateur and meilleur_score == 0:
        if role_utilisateur == 'agriculteur':
            reponse += "\n\nEn tant qu'agriculteur, vos fonctionnalités principales sont : publier des produits, recevoir et valider des commandes, et demander des livraisons."
        elif role_utilisateur == 'acheteur':
            reponse += "\n\nEn tant qu'acheteur, vos fonctionnalités principales sont : explorer le catalogue, passer des commandes et suivre vos livraisons."
        elif role_utilisateur == 'transporteur':
            reponse += "\n\nEn tant que transporteur, vos fonctionnalités principales sont : consulter les missions disponibles, les accepter et mettre à jour vos livraisons."

    return reponse


# ============================================================
# RECOMMANDATIONS — Filtrage basé sur le contenu
# ============================================================

def calculer_recommandations(acheteur, produits_disponibles, limite=6):
    """
    Algorithme de recommandation basé sur :
    1. Les catégories déjà achetées (score élevé)
    2. La popularité du produit (nombre de commandes)
    3. La fraîcheur (produits récemment publiés)
    4. Le bio si l'acheteur achète bio
    """
    from commandes.models import Commande

    commandes = Commande.objects.filter(
        acheteur=acheteur
    ).prefetch_related('lignes')

    categories_achetees = Counter()
    produits_deja_achetes = set()
    achete_bio = False

    for commande in commandes:
        for ligne in commande.lignes.all():
            produits_deja_achetes.add(ligne.produit.pk)
            if ligne.produit.categorie:
                categories_achetees[ligne.produit.categorie.pk] += 1
            if ligne.produit.est_bio:
                achete_bio = True

    produits_non_achetes = [
        p for p in produits_disponibles
        if p.pk not in produits_deja_achetes
    ]

    if not produits_non_achetes:
        produits_non_achetes = list(produits_disponibles)

    def score_produit(produit):
        score = 0

        # Catégorie déjà achetée
        if produit.categorie and produit.categorie.pk in categories_achetees:
            score += categories_achetees[produit.categorie.pk] * 30

        # Bonus bio
        if achete_bio and produit.est_bio:
            score += 20

        # Popularité (nombre de vues comme proxy)
        score += min(produit.nombre_vues * 0.5, 15)

        # Fraîcheur (produits récents)
        from django.utils import timezone
        from datetime import timedelta
        maintenant = timezone.now()
        age_jours = (maintenant - produit.date_publication).days
        if age_jours <= 3:
            score += 15
        elif age_jours <= 7:
            score += 10
        elif age_jours <= 30:
            score += 5

        return score

    produits_scores = [(p, score_produit(p)) for p in produits_non_achetes]
    produits_scores.sort(key=lambda x: x[1], reverse=True)

    def generer_raison(produit, score):
        if produit.categorie and produit.categorie.pk in categories_achetees:
            return f"Vous achetez souvent des {produit.categorie.nom.lower()}"
        if produit.est_bio and achete_bio:
            return "Produit bio comme vous les aimez"
        if produit.nombre_vues > 50:
            return "Très populaire sur la plateforme"
        from django.utils import timezone
        age = (timezone.now() - produit.date_publication).days
        if age <= 3:
            return "Fraîchement récolté et publié"
        return "Disponible près de chez vous"

    resultats = []
    for produit, score in produits_scores[:limite]:
        raison = generer_raison(produit, score)
        resultats.append((produit, raison))

    return resultats


# ============================================================
# MODÉRATION — Système de score automatique
# ============================================================

MOTS_INTERDITS = [
    'drogue', 'cocaine', 'heroine', 'cannabis', 'weed', 'arme', 'pistolet',
    'fusil', 'explosif', 'bombe', 'faux', 'contrefacon', 'illegal', 'fraude',
    'escroquerie', 'arnaque'
]

CATEGORIES_AUTORISEES = [
    'cereales', 'legumes', 'fruits', 'tubercules', 'legumineuses',
    'epices', 'produits laitiers', 'volailles', 'poissons', 'huiles',
    'manioc', 'mais', 'haricot', 'tomate', 'banane', 'igname',
    'soja', 'arachide', 'patate', 'chou', 'oignon', 'ail'
]


def analyser_produit_local(produit):
    """
    Analyse un produit selon des règles locales.
    Retourne (statut, raison) où statut est 'conforme', 'a_verifier' ou 'non_conforme'.
    """
    nom = _normaliser(produit.nom)
    description = _normaliser(produit.description)
    prix = float(produit.prix_unitaire)
    texte_complet = nom + ' ' + description

    # === VÉRIFICATION MOT INTERDIT ===
    for mot in MOTS_INTERDITS:
        if mot in texte_complet:
            return 'non_conforme', f"Mot interdit détecté : '{mot}'"

    # === VÉRIFICATION DESCRIPTION ===
    if len(produit.description.strip()) < 15:
        return 'a_verifier', "Description trop courte, difficile à évaluer"

    if len(produit.description.strip()) < 30:
        return 'a_verifier', "Description insuffisante pour les acheteurs"

    # === VÉRIFICATION PRIX ===
    if prix <= 0:
        return 'non_conforme', "Prix invalide (zéro ou négatif)"

    if prix < 10:
        return 'a_verifier', "Prix très bas, vérification recommandée"

    if prix > 500000:
        return 'a_verifier', "Prix très élevé, vérification recommandée"

    # === VÉRIFICATION NOM ===
    if len(produit.nom.strip()) < 3:
        return 'non_conforme', "Nom du produit trop court"

    if re.match(r'^[0-9\s]+$', produit.nom.strip()):
        return 'non_conforme', "Nom du produit invalide (que des chiffres)"

    # === VÉRIFICATION PHOTO ===
    if not produit.photos.exists():
        return 'a_verifier', "Aucune photo, les acheteurs préfèrent voir le produit"

    # === VÉRIFICATION QUANTITÉ ===
    if produit.quantite_disponible <= 0:
        return 'a_verifier', "Quantité disponible nulle ou invalide"

    # === VÉRIFICATION TEXTE RÉPÉTÉ ===
    mots = description.split()
    if len(mots) > 3:
        compteur = Counter(mots)
        mot_plus_frequent = compteur.most_common(1)[0]
        if mot_plus_frequent[1] > len(mots) * 0.5:
            return 'a_verifier', "Description suspecte : mots trop répétés"

    # === TOUT EST OK ===
    return 'conforme', "Annonce complète et cohérente"
    # ============================================================
# PRÉDICTION DE REVENUS
# ============================================================

import datetime
from collections import defaultdict


SAISONNALITE = {
    # Mois → coefficient multiplicateur de la demande
    # Basé sur les cycles agricoles camerounais
    1:  0.85,   # Janvier — saison sèche, demande modérée
    2:  0.80,   # Février — saison sèche, demande basse
    3:  0.90,   # Mars — début pluies, légère hausse
    4:  1.10,   # Avril — grande saison des pluies, forte demande
    5:  1.20,   # Mai — pic de la saison
    6:  1.15,   # Juin — bonne période
    7:  1.05,   # Juillet — période stable
    8:  1.00,   # Août — période normale
    9:  1.10,   # Septembre — retour des pluies
    10: 1.25,   # Octobre — pic de récolte, forte demande
    11: 1.20,   # Novembre — bonne période de vente
    12: 0.95,   # Décembre — fêtes, demande variable
}

TENDANCES_CATEGORIES = {
    # Catégorie → taux de croissance mensuel estimé
    'céréales':       0.03,
    'légumes':        0.05,
    'fruits':         0.04,
    'tubercules':     0.02,
    'légumineuses':   0.04,
    'épices':         0.06,
    'produits laitiers': 0.03,
    'volailles':      0.05,
    'poissons':       0.04,
    'huiles':         0.02,
}


def _coeff_saisonnalite(mois):
    return SAISONNALITE.get(mois, 1.0)


def _tendance_categorie(nom_categorie):
    nom = nom_categorie.lower() if nom_categorie else ''
    for cle, taux in TENDANCES_CATEGORIES.items():
        if cle in nom:
            return taux
    return 0.03  # taux par défaut


def _historique_ventes_produit(produit_id):
    """Récupère l'historique de ventes d'un produit sur les 12 derniers mois."""
    from commandes.models import LigneCommande
    from django.utils import timezone

    il_y_a_12_mois = timezone.now() - datetime.timedelta(days=365)
    lignes = LigneCommande.objects.filter(
        produit__id=produit_id,
        commande__statut__in=['validee', 'en_livraison', 'livree'],
        commande__date_commande__gte=il_y_a_12_mois,
    ).select_related('commande')

    ventes_par_mois = defaultdict(float)
    for ligne in lignes:
        mois = ligne.commande.date_commande.month
        ventes_par_mois[mois] += float(ligne.quantite)

    return dict(ventes_par_mois)


def _historique_ventes_categorie(categorie_id):
    """Récupère les ventes moyennes par mois pour une catégorie."""
    from commandes.models import LigneCommande
    from django.utils import timezone

    il_y_a_12_mois = timezone.now() - datetime.timedelta(days=365)
    lignes = LigneCommande.objects.filter(
        produit__categorie_id=categorie_id,
        commande__statut__in=['validee', 'en_livraison', 'livree'],
        commande__date_commande__gte=il_y_a_12_mois,
    ).select_related('commande', 'produit')

    ventes_par_mois = defaultdict(float)
    for ligne in lignes:
        mois = ligne.commande.date_commande.month
        ventes_par_mois[mois] += float(ligne.quantite)

    return dict(ventes_par_mois)


def predire_revenus(
    prix_unitaire,
    quantite_disponible,
    produit_id=None,
    categorie_id=None,
    nom_categorie=None,
    nb_mois=6,
):
    """
    Prédit les revenus potentiels sur nb_mois à venir.

    Retourne un dict avec :
    - predictions : liste de dicts par mois
    - total_optimiste / total_realiste / total_pessimiste
    - conseils : liste de recommandations textuelles
    """
    maintenant = datetime.datetime.now()
    tendance = _tendance_categorie(nom_categorie or '')
    commission = 0.03  # 3% commission AgriMarché

    # Historique de ventes
    histo_produit = {}
    histo_categorie = {}
    if produit_id:
        histo_produit = _historique_ventes_produit(produit_id)
    if categorie_id:
        histo_categorie = _historique_ventes_categorie(categorie_id)

    # Quantité de base mensuelle estimée
    # Si on a un historique, on l'utilise ; sinon on estime à 30% du stock par mois
    if histo_produit:
        base_mensuelle = sum(histo_produit.values()) / max(len(histo_produit), 1)
    elif histo_categorie:
        base_mensuelle = sum(histo_categorie.values()) / max(len(histo_categorie), 1)
        # Ajuster : ce produit représente environ 20% de la catégorie
        base_mensuelle *= 0.20
    else:
        # Aucun historique — estimation conservatrice
        base_mensuelle = quantite_disponible * 0.30

    # Limiter au stock disponible
    base_mensuelle = min(base_mensuelle, quantite_disponible)

    predictions = []
    total_optimiste = 0
    total_realiste = 0
    total_pessimiste = 0

    for i in range(nb_mois):
        mois_futur = (maintenant.month + i - 1) % 12 + 1
        annee_future = maintenant.year + (maintenant.month + i - 1) // 12
        nom_mois = _nom_mois(mois_futur)

        # Coefficient saisonnalité
        coeff_saison = _coeff_saisonnalite(mois_futur)

        # Coefficient tendance (croissance mensuelle)
        coeff_tendance = (1 + tendance) ** i

        # Quantité estimée vendue ce mois
        qte_realiste = base_mensuelle * coeff_saison * coeff_tendance
        qte_realiste = min(qte_realiste, quantite_disponible)

        qte_optimiste = qte_realiste * 1.30
        qte_pessimiste = qte_realiste * 0.70

        qte_optimiste = min(qte_optimiste, quantite_disponible)
        qte_pessimiste = min(qte_pessimiste, quantite_disponible)

        # Revenus bruts
        rev_realiste = qte_realiste * float(prix_unitaire)
        rev_optimiste = qte_optimiste * float(prix_unitaire)
        rev_pessimiste = qte_pessimiste * float(prix_unitaire)

        # Revenus nets (après commission)
        net_realiste = rev_realiste * (1 - commission)
        net_optimiste = rev_optimiste * (1 - commission)
        net_pessimiste = rev_pessimiste * (1 - commission)

        predictions.append({
            'mois': nom_mois,
            'mois_num': mois_futur,
            'annee': annee_future,
            'qte_estimee': round(qte_realiste, 1),
            'revenu_brut_realiste': round(rev_realiste),
            'revenu_net_realiste': round(net_realiste),
            'revenu_optimiste': round(net_optimiste),
            'revenu_pessimiste': round(net_pessimiste),
            'coeff_saison': coeff_saison,
        })

        total_optimiste += net_optimiste
        total_realiste += net_realiste
        total_pessimiste += net_pessimiste

    conseils = _generer_conseils(
        predictions=predictions,
        prix=float(prix_unitaire),
        qte=quantite_disponible,
        nom_categorie=nom_categorie,
    )

    return {
        'predictions': predictions,
        'total_optimiste': round(total_optimiste),
        'total_realiste': round(total_realiste),
        'total_pessimiste': round(total_pessimiste),
        'nb_mois': nb_mois,
        'commission': commission * 100,
        'conseils': conseils,
    }


def _nom_mois(num):
    noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    return noms[num - 1]


def _generer_conseils(predictions, prix, qte, nom_categorie):
    conseils = []

    # Trouver le meilleur mois
    meilleur = max(predictions, key=lambda x: x['revenu_net_realiste'])
    pire = min(predictions, key=lambda x: x['revenu_net_realiste'])

    conseils.append(
        f"📈 Votre meilleur mois sera <strong>{meilleur['mois']}</strong> "
        f"avec un revenu estimé de <strong>{meilleur['revenu_net_realiste']:,} CFA</strong>."
    )

    if pire['coeff_saison'] < 0.90:
        conseils.append(
            f"⚠️ En <strong>{pire['mois']}</strong> la demande baisse saisonnièrement. "
            f"Pensez à réduire vos prix de 10-15% pour écouler votre stock."
        )

    if qte > 500:
        conseils.append(
            "💡 Votre stock est important. Envisagez de le diviser en plusieurs annonces "
            "de plus petites quantités pour attirer plus d'acheteurs."
        )

    if prix < 200:
        conseils.append(
            "💰 Votre prix est bas. Si la qualité est bonne, "
            "une légère hausse de 10-20% n'affectera pas significativement vos ventes."
        )

    conseils.append(
        f"📱 Publiez votre annonce <strong>2 semaines avant {meilleur['mois']}</strong> "
        f"pour maximiser votre visibilité au bon moment."
    )

    return conseils


# ============================================================
# SUGGESTION DE PRIX OPTIMAL
# ============================================================

def suggerer_prix(
    nom_produit,
    categorie_id=None,
    quantite=None,
    est_bio=False,
    localisation=None,
):
    """
    Suggère un prix optimal basé sur les prix pratiqués sur la plateforme.
    Retourne (prix_min, prix_moyen, prix_max, conseil)
    """
    from produits.models import Produit
    from django.db.models import Avg, Min, Max

    filtre = {'statut': 'actif'}
    if categorie_id:
        filtre['categorie__id'] = categorie_id

    stats = Produit.objects.filter(**filtre).aggregate(
        prix_min=Min('prix_unitaire'),
        prix_moyen=Avg('prix_unitaire'),
        prix_max=Max('prix_unitaire'),
    )

    prix_min = float(stats['prix_min'] or 0)
    prix_moyen = float(stats['prix_moyen'] or 0)
    prix_max = float(stats['prix_max'] or 0)

    # Ajustements
    if est_bio:
        prix_moyen *= 1.20  # Bio vaut 20% de plus
        prix_min *= 1.10
        prix_max *= 1.25

    if not prix_moyen:
        # Aucun produit similaire — estimation générique
        prix_min = 100
        prix_moyen = 500
        prix_max = 2000
        conseil = "Aucun produit similaire trouvé. Fixez votre prix selon vos coûts de production."
    else:
        conseil = (
            f"Les produits similaires se vendent entre {round(prix_min)} et {round(prix_max)} CFA. "
            f"Nous recommandons {round(prix_moyen)} CFA pour rester compétitif."
        )

    return {
        'prix_min': round(prix_min),
        'prix_moyen': round(prix_moyen),
        'prix_max': round(prix_max),
        'conseil': conseil,
        'est_bio': est_bio,
    }


# ============================================================
# ANALYSE DE SENTIMENT DES ÉVALUATIONS
# ============================================================

MOTS_POSITIFS = [
    'excellent', 'parfait', 'super', 'très bien', 'top', 'bravo', 'merci',
    'satisfait', 'recommande', 'qualité', 'frais', 'bon', 'rapide', 'ponctuel',
    'sérieux', 'professionnel', 'agréable', 'content', 'heureux', 'génial',
    'impeccable', 'propre', 'conforme', 'livré', 'délai', 'correct',
]

MOTS_NEGATIFS = [
    'mauvais', 'nul', 'horrible', 'déçu', 'problème', 'retard', 'abîmé',
    'pourri', 'sale', 'décomposé', 'pas frais', 'cassé', 'manquant',
    'incomplet', 'tard', 'jamais', 'pas conforme', 'arnaque', 'voleur',
    'non conforme', 'déception', 'insatisfait', 'mauvaise', 'absent',
]

MOTS_INTENSIFICATEURS = ['très', 'vraiment', 'tellement', 'extrêmement', 'super', 'trop']


def analyser_sentiment(texte):
    """
    Analyse le sentiment d'un commentaire.
    Retourne ('positif'|'neutre'|'negatif', score -100 à 100, mots_detectes)
    """
    if not texte or len(texte.strip()) < 3:
        return 'neutre', 0, []

    texte_norm = _normaliser(texte)
    mots = texte_norm.split()
    score = 0
    mots_detectes = []

    for i, mot in enumerate(mots):
        intensif = mots[i - 1] in MOTS_INTENSIFICATEURS if i > 0 else False
        multiplicateur = 1.5 if intensif else 1.0

        for pos in MOTS_POSITIFS:
            if pos in texte_norm:
                score += 15 * multiplicateur
                mots_detectes.append(f"+{pos}")
                break

        for neg in MOTS_NEGATIFS:
            if neg in texte_norm:
                score -= 15 * multiplicateur
                mots_detectes.append(f"-{neg}")
                break

    score = max(-100, min(100, score))

    if score >= 20:
        sentiment = 'positif'
    elif score <= -20:
        sentiment = 'negatif'
    else:
        sentiment = 'neutre'

    return sentiment, round(score), list(set(mots_detectes))


# ============================================================
# SCORE DE FIABILITÉ TRANSPORTEUR
# ============================================================

def calculer_score_fiabilite_transporteur(profil_transporteur):
    """
    Calcule un score de fiabilité 0-100 pour un transporteur.
    Critères :
    - Taux de livraisons réussies (40%)
    - Note moyenne (25%)
    - Réactivité (temps d'acceptation) (15%)
    - Ancienneté (10%)
    - Absence de litiges (10%)
    """
    from livraisons.models import Livraison
    from django.utils import timezone

    livraisons = Livraison.objects.filter(transporteur=profil_transporteur)
    total = livraisons.count()

    if total == 0:
        return {
            'score': 50,
            'label': 'Nouveau transporteur',
            'details': {
                'taux_reussite': 0,
                'note_moyenne': profil_transporteur.note_moyenne or 0,
                'nb_livraisons': 0,
            },
            'badge': 'nouveau',
        }

    livrees = livraisons.filter(statut='livree').count()
    taux_reussite = (livrees / total) * 100

    note = float(profil_transporteur.note_moyenne or 0)

    # Score ancienneté
    anciennete_jours = (timezone.now() - profil_transporteur.utilisateur.date_inscription).days
    score_anciennete = min(anciennete_jours / 365 * 100, 100)

    # Score global
    score = (
        taux_reussite * 0.40 +
        (note / 5 * 100) * 0.25 +
        score_anciennete * 0.10 +
        min(total * 2, 100) * 0.15 +
        100 * 0.10  # pas de litiges par défaut
    )

    score = round(min(score, 100))

    if score >= 85:
        label = 'Excellent transporteur'
        badge = 'or'
    elif score >= 70:
        label = 'Bon transporteur'
        badge = 'argent'
    elif score >= 50:
        label = 'Transporteur fiable'
        badge = 'bronze'
    else:
        label = 'Transporteur débutant'
        badge = 'standard'

    return {
        'score': score,
        'label': label,
        'badge': badge,
        'details': {
            'taux_reussite': round(taux_reussite, 1),
            'note_moyenne': note,
            'nb_livraisons': total,
            'nb_livrees': livrees,
        },
    }


# ============================================================
# PRÉVISION DEMANDE PAR CATÉGORIE
# ============================================================

def prevoir_demande_categorie(categorie_id, nb_mois=3):
    """
    Prédit la demande (nombre de commandes) pour une catégorie sur les prochains mois.
    """
    from commandes.models import LigneCommande
    from django.utils import timezone

    maintenant = timezone.now()
    il_y_a_6_mois = maintenant - datetime.timedelta(days=180)

    lignes = LigneCommande.objects.filter(
        produit__categorie_id=categorie_id,
        commande__statut__in=['validee', 'en_livraison', 'livree'],
        commande__date_commande__gte=il_y_a_6_mois,
    )

    commandes_par_mois = defaultdict(int)
    for ligne in lignes:
        mois = ligne.commande.date_commande.month
        commandes_par_mois[mois] += 1

    moyenne_mensuelle = sum(commandes_par_mois.values()) / max(len(commandes_par_mois), 1)

    predictions = []
    for i in range(nb_mois):
        mois_futur = (maintenant.month + i - 1) % 12 + 1
        coeff = _coeff_saisonnalite(mois_futur)
        nb_prevu = round(moyenne_mensuelle * coeff)
        predictions.append({
            'mois': _nom_mois(mois_futur),
            'nb_commandes_prevu': nb_prevu,
            'tendance': 'hausse' if coeff > 1 else 'baisse' if coeff < 0.95 else 'stable',
        })

    return predictions


# ============================================================
# DÉTECTION AGRICULTEURS INACTIFS
# ============================================================

def detecter_agriculteurs_inactifs(jours_seuil=30):
    """
    Retourne la liste des agriculteurs qui n'ont pas eu de ventes
    depuis jours_seuil jours, avec suggestions d'amélioration.
    """
    from accounts.models import ProfilAgriculteur
    from commandes.models import Commande
    from django.utils import timezone

    seuil = timezone.now() - datetime.timedelta(days=jours_seuil)

    agriculteurs = ProfilAgriculteur.objects.prefetch_related(
        'produits', 'utilisateur'
    )

    inactifs = []

    for agri in agriculteurs:
        derniere_vente = Commande.objects.filter(
            agriculteur=agri,
            statut__in=['validee', 'en_livraison', 'livree'],
        ).order_by('-date_commande').first()

        est_inactif = (
            derniere_vente is None or
            derniere_vente.date_commande < seuil
        )

        if est_inactif:
            suggestions = _suggestions_reactivation(agri, derniere_vente)
            inactifs.append({
                'agriculteur_id': agri.pk,
                'nom': agri.utilisateur.get_full_name(),
                'email': agri.utilisateur.email,
                'derniere_vente': derniere_vente.date_commande if derniere_vente else None,
                'nb_produits_actifs': agri.produits.filter(statut='actif').count(),
                'suggestions': suggestions,
            })

    return inactifs


def _suggestions_reactivation(profil, derniere_vente):
    suggestions = []
    produits_actifs = profil.produits.filter(statut='actif').count()
    produits_total = profil.produits.count()

    if produits_actifs == 0 and produits_total > 0:
        suggestions.append("Vos produits sont hors stock ou en attente — mettez à jour vos annonces.")
    elif produits_actifs == 0:
        suggestions.append("Publiez votre première annonce pour commencer à vendre.")
    elif produits_actifs < 3:
        suggestions.append("Ajoutez plus de produits pour attirer plus d'acheteurs.")

    if profil.note_moyenne and profil.note_moyenne < 3:
        suggestions.append("Votre note est basse. Améliorez la qualité et la rapidité de vos réponses.")

    if derniere_vente is None:
        suggestions.append("Commencez par baisser légèrement vos prix pour attirer vos premiers acheteurs.")

    if not profil.localisation:
        suggestions.append("Ajoutez votre localisation pour apparaître dans les recherches locales.")

    if not suggestions:
        suggestions.append("Mettez à jour vos photos pour rendre vos annonces plus attractives.")

    return suggestions