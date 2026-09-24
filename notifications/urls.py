from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_notifications, name='liste_notifications'),
    path('<int:pk>/aller/', views.aller_vers_notification, name='aller_vers_notification'),
]