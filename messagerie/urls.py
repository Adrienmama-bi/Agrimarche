from . import views
from django.urls import path

urlpatterns = [
    path('', views.boite_reception, name='boite_reception'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('demarrer/<int:utilisateur_id>/', views.demarrer_conversation, name='demarrer_conversation'),
]