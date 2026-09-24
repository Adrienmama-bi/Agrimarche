"""
Tests des fonctionnalités de gestion des produits
"""
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Utilisateur, ProfilAgriculteur, ProfilAcheteur
from produits.models import Produit, Categorie


class TestProduits(TestCase):

    def setUp(self):
        self.client = Client()

        # Créer un agriculteur
        self.agriculteur_user = Utilisateur.objects.create_user(
            username='agriculteur', password='Test123!', role='agriculteur',
            first_name='Jean', last_name='Agriculteur'
        )
        self.profil_agriculteur = ProfilAgriculteur.objects.create(
            utilisateur=self.agriculteur_user,
            exploitation='Ferme Test',
            localisation='Kinshasa',
        )

        # Créer un acheteur
        self.acheteur_user = Utilisateur.objects.create_user(
            username='acheteur', password='Test123!', role='acheteur',
            first_name='Marie', last_name='Acheteur'
        )
        self.profil_acheteur = ProfilAcheteur.objects.create(
            utilisateur=self.acheteur_user,
            adresse_livraison='Avenue Test, Kinshasa'
        )

        # Créer une catégorie
        self.categorie = Categorie.objects.create(nom='Céréales', icone='🌽')

        # Créer un produit actif
        self.produit = Produit.objects.create(
            agriculteur=self.profil_agriculteur,
            categorie=self.categorie,
            nom='Maïs frais',
            description='Du maïs frais récolté ce matin de qualité supérieure',
            prix_unitaire=450,
            unite='kg',
            quantite_disponible=100,
            statut='actif',
        )

    def test_catalogue_accessible_sans_connexion(self):
        """Le catalogue est visible par tous, même non connectés."""
        response = self.client.get(reverse('catalogue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maïs frais')

    def test_catalogue_filtre_par_categorie(self):
        """Le filtre par catégorie fonctionne correctement."""
        response = self.client.get(reverse('catalogue'), {'categorie': self.categorie.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maïs frais')

    def test_catalogue_recherche(self):
        """La recherche par mot-clé fonctionne."""
        response = self.client.get(reverse('catalogue'), {'q': 'Maïs'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maïs frais')

    def test_catalogue_recherche_sans_resultat(self):
        """Une recherche sans résultat affiche l'état vide."""
        response = self.client.get(reverse('catalogue'), {'q': 'produit_inexistant_xyz'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Maïs frais')

    def test_detail_produit_accessible(self):
        """La page de détail d'un produit actif est accessible."""
        response = self.client.get(reverse('detail_produit', args=[self.produit.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maïs frais')
        self.assertContains(response, '450')

    def test_detail_produit_inexistant(self):
        """Accéder à un produit inexistant renvoie une 404."""
        response = self.client.get(reverse('detail_produit', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_publier_produit_agriculteur(self):
        """Un agriculteur peut publier un produit."""
        self.client.login(username='agriculteur', password='Test123!')
        response = self.client.post(reverse('publier_produit'), {
            'nom': 'Manioc frais',
            'description': 'Manioc de qualité supérieure cultivé sans pesticides',
            'prix_unitaire': '300',
            'unite': 'kg',
            'quantite_disponible': '200',
            'quantite_min_commande': '5',
            'localisation': 'Kinshasa',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Produit.objects.filter(nom='Manioc frais').exists())
        produit = Produit.objects.get(nom='Manioc frais')
        self.assertEqual(produit.statut, 'en_attente')

    def test_publier_produit_non_agriculteur(self):
        """Un acheteur ne peut pas publier un produit."""
        self.client.login(username='acheteur', password='Test123!')
        response = self.client.get(reverse('publier_produit'))
        self.assertEqual(response.status_code, 302)

    def test_catalogue_ne_montre_pas_produits_en_attente(self):
        """Les produits en attente de validation n'apparaissent pas dans le catalogue."""
        produit_en_attente = Produit.objects.create(
            agriculteur=self.profil_agriculteur,
            nom='Produit en attente',
            description='Ce produit ne doit pas être visible dans le catalogue',
            prix_unitaire=100,
            unite='kg',
            quantite_disponible=50,
            statut='en_attente',
        )
        response = self.client.get(reverse('catalogue'))
        self.assertNotContains(response, 'Produit en attente')

    def test_produit_est_disponible(self):
        """La méthode est_disponible retourne True pour un produit actif avec stock."""
        self.assertTrue(self.produit.est_disponible())

    def test_produit_epuise_non_disponible(self):
        """Un produit avec stock nul n'est pas disponible."""
        self.produit.quantite_disponible = 0
        self.produit.save()
        self.assertFalse(self.produit.est_disponible())