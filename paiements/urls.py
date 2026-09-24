from django.urls import path
from . import views

urlpatterns = [
    path('payer/<int:commande_id>/', views.payer_commande, name='payer_commande'),
    path('confirmer/<int:pk>/', views.confirmer_paiement, name='confirmer_paiement'),
    path('recu/<int:pk>/', views.recu_paiement, name='recu_paiement'),
    path('mes-paiements/', views.mes_paiements, name='mes_paiements'),
]