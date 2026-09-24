from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('agriculteur', 'Agriculteur'),
        ('acheteur', 'Acheteur'),
        ('transporteur', 'Transporteur'),
        ('admin', 'Administrateur'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('banni', 'Banni'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    date_inscription = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def est_agriculteur(self):
        return self.role == 'agriculteur'

    @property
    def est_acheteur(self):
        return self.role == 'acheteur'

    @property
    def est_transporteur(self):
        return self.role == 'transporteur'

    @property
    def est_admin(self):
        return self.role == 'admin'


class ProfilAgriculteur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='profil_agriculteur')
    exploitation = models.CharField(max_length=200)
    localisation = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    superficie = models.FloatField(null=True, blank=True)
    types_production = models.TextField(blank=True)
    note_moyenne = models.FloatField(default=0.0)
    est_verifie = models.BooleanField(default=False)
    revenus_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    rayon_livraison_km = models.IntegerField(default=50)

    def _str_(self):
        return f"Profil de {self.utilisateur.get_full_name()}"


class ProfilAcheteur(models.Model):
    TYPE_CHOICES = [
        ('particulier', 'Particulier'),
        ('revendeur', 'Revendeur'),
        ('restaurant', 'Restaurant'),
        ('supermarche', 'Supermarché'),
    ]
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='profil_acheteur')
    adresse_livraison = models.CharField(max_length=300, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    type_acheteur = models.CharField(max_length=20, choices=TYPE_CHOICES, default='particulier')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


    def _str_(self):
        return f"Profil de {self.utilisateur.get_full_name()}"


class ProfilTransporteur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='profil_transporteur')
    latitude_actuelle = models.FloatField(null=True, blank=True)
    longitude_actuelle = models.FloatField(null=True, blank=True)
    zone_couverture = models.TextField(blank=True)
    disponible = models.BooleanField(default=True)
    note_moyenne = models.FloatField(default=0.0)
    revenus_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    est_verifie = models.BooleanField(default=False)
    numero_permis = models.CharField(max_length=50, blank=True)
    latitude_actuelle = models.FloatField(null=True, blank=True)
    longitude_actuelle = models.FloatField(null=True, blank=True)

    def _str_(self):
        return f"Profil de {self.utilisateur.get_full_name()}"


class Vehicule(models.Model):
    TYPE_CHOICES = [
        ('camion', 'Camion'),
        ('moto', 'Moto'),
        ('voiture', 'Voiture'),
        ('tracteur', 'Tracteur'),
        ('camionnette', 'Camionnette'),
    ]
    transporteur = models.ForeignKey(ProfilTransporteur, on_delete=models.CASCADE, related_name='vehicules')
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    immatriculation = models.CharField(max_length=30, unique=True)
    capacite_kg = models.FloatField()
    est_refrigere = models.BooleanField(default=False)
    annee = models.IntegerField()
    photo = models.ImageField(upload_to='vehicules/', blank=True, null=True)
    est_actif = models.BooleanField(default=True)

    def _str_(self):
        return f"{self.type_vehicule} — {self.immatriculation}"