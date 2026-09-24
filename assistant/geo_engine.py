"""
Moteur de géolocalisation AgriMarché
Utilise la formule de Haversine pour calculer les distances
et l'algorithme du voisin le plus proche pour optimiser les itinéraires.
100% local, sans API payante.
"""

import math
from itertools import permutations


# ============================================================
# FORMULE DE HAVERSINE — Distance entre deux points GPS
# ============================================================

def distance_km(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en km entre deux points GPS
    en utilisant la formule de Haversine.
    """
    R = 6371  # Rayon de la Terre en km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) * 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) * 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def duree_estimee_minutes(distance_km_val, vitesse_kmh=40):
    """
    Estime la durée de trajet en minutes.
    Vitesse par défaut 40 km/h (trafic urbain camerounais).
    """
    return round((distance_km_val / vitesse_kmh) * 60)


# ============================================================
# PRODUITS PROCHES — Filtrage par distance
# ============================================================

def produits_proches(lat_acheteur, lon_acheteur, produits, rayon_km=50):
    """
    Filtre et trie les produits par distance croissante
    par rapport à la position de l'acheteur.
    """
    resultats = []

    for produit in produits:
        if produit.latitude and produit.longitude:
            dist = distance_km(
                lat_acheteur, lon_acheteur,
                produit.latitude, produit.longitude
            )
            if dist <= rayon_km:
                resultats.append({
                    'produit': produit,
                    'distance_km': round(dist, 1),
                    'duree_minutes': duree_estimee_minutes(dist),
                })
        else:
            # Produit sans coordonnées — inclure sans distance
            resultats.append({
                'produit': produit,
                'distance_km': None,
                'duree_minutes': None,
            })

    # Trier : produits avec coordonnées d'abord, par distance croissante
    resultats.sort(key=lambda x: (x['distance_km'] is None, x['distance_km'] or 9999))
    return render(request, 'assistant/produits_proches.html', {
    'resultats': resultats[:20],
    'position_connue': True,
    'rayon': rayon,
    'rayons': [10, 25, 50, 100, 200],
    'lat_acheteur': profil.latitude,
    'lng_acheteur': profil.longitude,
    'markers_json': json.dumps(markers),
})


def agriculteurs_proches(lat, lon, agriculteurs, rayon_km=100):
    """
    Retourne les agriculteurs triés par distance.
    """
    resultats = []

    for agri in agriculteurs:
        if agri.latitude and agri.longitude:
            dist = distance_km(lat, lon, agri.latitude, agri.longitude)
            if dist <= rayon_km:
                resultats.append({
                    'agriculteur': agri,
                    'distance_km': round(dist, 1),
                    'duree_minutes': duree_estimee_minutes(dist),
                })

    resultats.sort(key=lambda x: x['distance_km'])
    return resultats


# ============================================================
# ITINÉRAIRE OPTIMAL — Algorithme du voisin le plus proche
# ============================================================

def optimiser_itineraire(position_depart, livraisons):
    """
    Calcule l'ordre optimal de livraisons pour un transporteur.
    Utilise l'algorithme du voisin le plus proche (greedy).

    position_depart : dict {'lat': float, 'lng': float}
    livraisons : liste de dicts {
        'id': int,
        'lat_dest': float,
        'lng_dest': float,
        'adresse': str,
        'commande_id': int,
        'acheteur_nom': str,
    }

    Retourne l'ordre optimisé avec distances et durées.
    """
    if not livraisons:
        return {
            'ordre': [],
            'distance_totale_km': 0,
            'duree_totale_minutes': 0,
        }

    # Pour les petits nombres (≤ 6), on peut faire une recherche exhaustive
    if len(livraisons) <= 6:
        return _optimiser_exhaustif(position_depart, livraisons)

    # Pour les grands nombres, on utilise le voisin le plus proche
    return _optimiser_greedy(position_depart, livraisons)


def _optimiser_greedy(pos_depart, livraisons):
    """Algorithme du voisin le plus proche."""
    restantes = list(livraisons)
    ordre = []
    pos_actuelle = pos_depart
    distance_totale = 0
    duree_totale = 0

    while restantes:
        # Trouver la livraison la plus proche
        plus_proche = None
        dist_min = float('inf')

        for liv in restantes:
            if liv.get('lat_dest') and liv.get('lng_dest'):
                dist = distance_km(
                    pos_actuelle['lat'], pos_actuelle['lng'],
                    liv['lat_dest'], liv['lng_dest']
                )
                if dist < dist_min:
                    dist_min = dist
                    plus_proche = liv

        if plus_proche is None:
            # Livraison sans coordonnées — ajouter à la fin
            plus_proche = restantes[0]
            dist_min = 0

        duree = duree_estimee_minutes(dist_min)
        ordre.append({
            **plus_proche,
            'distance_km': round(dist_min, 1),
            'duree_minutes': duree,
            'ordre_num': len(ordre) + 1,
        })

        distance_totale += dist_min
        duree_totale += duree
        pos_actuelle = {
            'lat': plus_proche.get('lat_dest', pos_actuelle['lat']),
            'lng': plus_proche.get('lng_dest', pos_actuelle['lng']),
        }
        restantes.remove(plus_proche)

    return {
        'ordre': ordre,
        'distance_totale_km': round(distance_totale, 1),
        'duree_totale_minutes': duree_totale,
        'economie_estimee': _calculer_economie(livraisons, distance_totale),
    }


def _optimiser_exhaustif(pos_depart, livraisons):
    """Recherche exhaustive pour ≤ 6 livraisons."""
    meilleure_distance = float('inf')
    meilleur_ordre = None

    for perm in permutations(livraisons):
        dist_totale = 0
        pos = pos_depart

        for liv in perm:
            if liv.get('lat_dest') and liv.get('lng_dest'):
                dist_totale += distance_km(
                    pos['lat'], pos['lng'],
                    liv['lat_dest'], liv['lng_dest']
                )
                pos = {'lat': liv['lat_dest'], 'lng': liv['lng_dest']}

        if dist_totale < meilleure_distance:
            meilleure_distance = dist_totale
            meilleur_ordre = list(perm)

    if meilleur_ordre is None:
        return {'ordre': [], 'distance_totale_km': 0, 'duree_totale_minutes': 0}

    ordre_final = []
    pos = pos_depart
    dist_totale = 0

    for i, liv in enumerate(meilleur_ordre):
        if liv.get('lat_dest') and liv.get('lng_dest'):
            dist = distance_km(
                pos['lat'], pos['lng'],
                liv['lat_dest'], liv['lng_dest']
            )
        else:
            dist = 0

        duree = duree_estimee_minutes(dist)
        dist_totale += dist
        ordre_final.append({
            **liv,
            'distance_km': round(dist, 1),
            'duree_minutes': duree,
            'ordre_num': i + 1,
        })
        pos = {'lat': liv.get('lat_dest', pos['lat']), 'lng': liv.get('lng_dest', pos['lng'])}

    return {
        'ordre': ordre_final,
        'distance_totale_km': round(dist_totale, 1),
        'duree_totale_minutes': duree_estimee_minutes(dist_totale),
        'economie_estimee': _calculer_economie(livraisons, dist_totale),
    }


def _calculer_economie(livraisons, distance_optimisee):
    """Estime l'économie de carburant par rapport à un ordre aléatoire."""
    # Distance si on faisait les livraisons dans l'ordre original
    distance_aleatoire = distance_optimisee * 1.3  # 30% de plus en moyenne
    economie_km = distance_aleatoire - distance_optimisee
    # 1L de carburant = ~10 km, 1L = ~750 CFA
    economie_cfa = round((economie_km / 10) * 750)
    return {
        'km_economises': round(economie_km, 1),
        'carburant_economise_cfa': economie_cfa,
    }


# ============================================================
# GÉOCODAGE SIMPLE — Nom de ville → Coordonnées Cameroun
# ============================================================

# Base de données des villes camerounaises principales
VILLES_CAMEROUN = {
    'yaoundé': (-3.8480, 11.5021),
    'yaounde': (-3.8480, 11.5021),
    'douala': (4.0511, 9.7679),
    'bamenda': (5.9527, 10.1457),
    'bafoussam': (5.4737, 10.4179),
    'garoua': (9.3014, 13.3928),
    'maroua': (10.5904, 14.3160),
    'ngaoundéré': (7.3226, 13.5840),
    'ngaoundere': (7.3226, 13.5840),
    'bertoua': (4.5788, 13.6863),
    'ebolowa': (2.9000, 11.1500),
    'kribi': (2.9380, 9.9087),
    'limbe': (4.0142, 9.2059),
    'kumba': (4.6364, 9.4470),
    'nkongsamba': (4.9523, 9.9338),
    'edéa': (3.7958, 10.1292),
    'edea': (3.7958, 10.1292),
    'mbalmayo': (3.5137, 11.5020),
    'sangmélima': (2.9313, 11.9812),
    'sangmelima': (2.9313, 11.9812),
    'obala': (4.1667, 11.5333),
    'eseka': (3.6500, 10.7667),
}


def geocoder_ville(texte):
    """
    Tente de trouver les coordonnées d'une ville camerounaise
    à partir d'un texte (nom de ville, adresse...).
    Retourne (lat, lng) ou (None, None) si non trouvé.
    """
    if not texte:
        return None, None

    texte_norm = texte.lower().strip()

    for ville, coords in VILLES_CAMEROUN.items():
        if ville in texte_norm:
            return coords

    return None, None


def enrichir_produit_coords(produit):
    """
    Tente d'ajouter les coordonnées GPS à un produit
    en se basant sur sa localisation textuelle.
    """
    if produit.latitude and produit.longitude:
        return True  # Déjà géocodé

    # Essayer depuis la localisation du produit
    lat, lng = geocoder_ville(produit.localisation)

    if lat is None:
        # Essayer depuis la localisation de l'agriculteur
        lat, lng = geocoder_ville(produit.agriculteur.localisation)

    if lat is None:
        return False

    produit.latitude = lat
    produit.longitude = lng
    produit.save(update_fields=['latitude', 'longitude'])
    return True


def enrichir_profil_agriculteur(profil):
    """
    Géocode automatiquement un profil agriculteur
    depuis sa localisation textuelle.
    """
    if profil.latitude and profil.longitude:
        return True

    lat, lng = geocoder_ville(profil.localisation or '')
    if lat:
        profil.latitude = lat
        profil.longitude = lng
        profil.save(update_fields=['latitude', 'longitude'])
        return True
    return False