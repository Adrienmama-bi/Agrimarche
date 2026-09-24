from django.urls import path
from . import views

urlpatterns = [
    path('missions/', views.missions_disponibles, name='missions_disponibles'),
    path('missions/<int:pk>/accepter/', views.accepter_mission, name='accepter_mission'),
    path('mes-livraisons/', views.mes_livraisons, name='mes_livraisons'),
    path('<int:pk>/', views.detail_livraison, name='detail_livraison'),
    path('<int:pk>/statut/<str:nouveau_statut>/', views.mettre_a_jour_statut, name='mettre_a_jour_statut'),
    path('<int:pk>/position/maj/', views.mettre_a_jour_position, name='mettre_a_jour_position'),
    path('<int:pk>/position/', views.position_livraison, name='position_livraison'),
]