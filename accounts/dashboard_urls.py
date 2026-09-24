from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agriculteur/', views.dashboard_agriculteur, name='dashboard_agriculteur'),
    path('acheteur/', views.dashboard_acheteur, name='dashboard_acheteur'),
    path('transporteur/', views.dashboard_transporteur, name='dashboard_transporteur'),
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/moderation/', views.moderation_produits, name='moderation_produits'),
    path('admin/moderation/<int:pk>/valider/', views.valider_produit_admin, name='valider_produit_admin'),
    path('admin/moderation/<int:pk>/refuser/', views.refuser_produit_admin, name='refuser_produit_admin'),
    path('admin/utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('admin/utilisateurs/<int:pk>/suspendre/', views.suspendre_utilisateur, name='suspendre_utilisateur'),
    path('profil/', views.mon_profil, name='mon_profil'),
    path('vehicules/', views.gestion_vehicules, name='gestion_vehicules'),
    path('vehicules/ajouter/', views.ajouter_vehicule, name='ajouter_vehicule'),
    path('vehicules/<int:pk>/supprimer/', views.supprimer_vehicule, name='supprimer_vehicule'),
]