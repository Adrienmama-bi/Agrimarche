from django.db import models
from accounts.models import ProfilAgriculteur


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True)
    categorie_parente = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sous_categories')

    def _str_(self):
        return self.nom


class Produit(models.Model):
    UNITE_CHOICES = [
        ('kg', 'Kilogramme'), ('tonne', 'Tonne'), ('sac', 'Sac'),
        ('litre', 'Litre'), ('piece', 'Pièce'), ('botte', 'Botte'), ('caisse', 'Caisse'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'), ('vendu', 'Épuisé'),
        ('suspendu', 'Suspendu'), ('en_attente', 'En attente de validation'),
    ]

    agriculteur = models.ForeignKey(ProfilAgriculteur, on_delete=models.CASCADE, related_name='produits')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='produits')
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    unite = models.CharField(max_length=20, choices=UNITE_CHOICES, default='kg')
    quantite_disponible = models.FloatField()
    quantite_min_commande = models.FloatField(default=1)
    date_recolte = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    est_bio = models.BooleanField(default=False)
    localisation = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    nombre_vues = models.IntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-date_publication']

    def _str_(self):
        return f"{self.nom} — {self.agriculteur.utilisateur.get_full_name()}"

    def est_disponible(self):
        return self.statut == 'actif' and self.quantite_disponible > 0


class PhotoProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='produits/')
    est_principale = models.BooleanField(default=False)
    ordre = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordre']