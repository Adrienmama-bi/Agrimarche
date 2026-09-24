from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.chat_widget_data, name='chat_widget_data'),
    path('envoyer/', views.envoyer_message_chat, name='envoyer_message_chat'),


    # IA avancée
    path('prediction-revenus/', views.prediction_revenus, name='prediction_revenus'),
    path('suggerer-prix/', views.suggerer_prix_view, name='suggerer_prix'),
    path('score-transporteur/<int:transporteur_id>/', views.score_fiabilite_view, name='score_fiabilite'),
    path('demande-categorie/', views.demande_categorie_view, name='demande_categorie'),
    path('agriculteurs-inactifs/', views.agriculteurs_inactifs_view, name='agriculteurs_inactifs'),

         # Géolocalisation
    path('carte/catalogue/', views.carte_catalogue, name='carte_catalogue'),
    path('carte/agriculteurs/', views.carte_agriculteurs, name='carte_agriculteurs'),
    path('carte/produits-proches/', views.produits_proches_view, name='produits_proches'),
    path('carte/itineraire/', views.itineraire_optimal_view, name='itineraire_optimal'),
    path('position/maj/', views.maj_position_utilisateur, name='maj_position'),
    path('geocoder/', views.geocoder_adresse, name='geocoder_adresse'),
    
]