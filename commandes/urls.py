from django.urls import path
from . import views

urlpatterns = [
    path('passer/<int:produit_id>/', views.passer_commande, name='passer_commande'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('<int:pk>/', views.detail_commande, name='detail_commande'),
    path('recues/', views.commandes_recues, name='commandes_recues'),
    path('<int:pk>/valider/', views.valider_commande, name='valider_commande'),
    path('<int:pk>/refuser/', views.refuser_commande, name='refuser_commande'),
    path('<int:pk>/evaluer/', views.evaluer_commande, name='evaluer_commande'),
    path('mes-avis/', views.mes_avis, name='mes_avis'),
]