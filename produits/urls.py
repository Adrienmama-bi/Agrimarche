from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('produit/<int:pk>/', views.detail_produit, name='detail_produit'),
    path('publier/', views.publier_produit, name='publier_produit'),
    path('mes-produits/', views.mes_produits, name='mes_produits'),
    path('produit/<int:pk>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('produit/<int:pk>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
]