"""
Tests des fonctionnalités de commande
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Utilisateur, ProfilAgriculteur, ProfilAcheteur
from produits.models import Produit, Categorie
from commandes.models import Commande, LigneCommande


class TestCommandes(TestCase):

    def setUp(self):
        self.client = Client()

        self.agriculteur_user = Utilisateur.objects.create_user(
            username='agriculteur', password='Test123!', role='agriculteur',
            first_name='Jean', last_name='Agriculteur'
        )
        self.profil_agriculteur = ProfilAgriculteur.objects.create(
            utilisateur=self.agriculteur_user,
            exploitation='Ferme Test',
            localisation='Kinshasa',
        )

        self.acheteur_user = Utilisateur.objects.create_user(
            username='acheteur', password='Test123!', role='acheteur',
            first_name='Marie', last_name='Acheteur'
        )
        self.profil_acheteur = ProfilAcheteur.objects.create(
            utilisateur=self.acheteur_user,
            adresse_livraison='Avenue Test, Kinshasa'
        )

        self.categorie = Categorie.objects.create(nom='Céréales', icone='🌽')

        self.produit = Produit.objects.create(
            agriculteur=self.profil_agriculteur,
            categorie=self.categorie,
            nom='Maïs frais',
            description='Maïs frais de qualité supérieure',
            prix_unitaire=Decimal('450'),
            unite='kg',
            quantite_disponible=100,
            quantite_min_commande=5,
            statut='actif',
        )

    def test_passer_commande_acheteur(self):
        """Un acheteur peut passer une commande sur un produit actif."""
        self.client.login(username='acheteur', password='Test123!')
        response = self.client.post(reverse('passer_commande', args=[self.produit.pk]), {
            'quantite': '10',
            'adresse': 'Avenue Test, Kinshasa',
            'date_livraison': '2026-12-01',
            'notes': 'Livraison le matin svp',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Commande.objects.filter(acheteur=self.profil_acheteur).exists())

    def test_stock_diminue_apres_commande(self):
        """Le stock du produit diminue après une commande."""
        self.client.login(username='acheteur', password='Test123!')
        self.client.post(reverse('passer_commande', args=[self.produit.pk]), {
            'quantite': '10',
            'adresse': 'Avenue Test, Kinshasa',
        })
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.quantite_disponible, 90)

    def test_commande_quantite_insuffisante(self):
        """Une commande échoue si la quantité dépasse le stock."""
        self.client.login(username='acheteur', password='Test123!')
        response = self.client.post(reverse('passer_commande', args=[self.produit.pk]), {
            'quantite': '999',
            'adresse': 'Avenue Test, Kinshasa',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Commande.objects.filter(acheteur=self.profil_acheteur).exists())

    def test_commande_quantite_minimum(self):
        """Une commande échoue si la quantité est inférieure au minimum."""
        self.client.login(username='acheteur', password='Test123!')
        response = self.client.post(reverse('passer_commande', args=[self.produit.pk]), {
            'quantite': '1',
            'adresse': 'Avenue Test, Kinshasa',
        })
        self.assertFalse(Commande.objects.filter(acheteur=self.profil_acheteur).exists())

    def test_commande_non_acheteur_impossible(self):
        """Un agriculteur ne peut pas passer de commande."""
        self.client.login(username='agriculteur', password='Test123!')
        response = self.client.post(reverse('passer_commande', args=[self.produit.pk]), {
            'quantite': '10',
            'adresse': 'Avenue Test, Kinshasa',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Commande.objects.filter(agriculteur=self.profil_agriculteur).exists())

    def test_valider_commande_agriculteur(self):
        """Un agriculteur peut valider une commande reçue."""
        commande = Commande.objects.create(
            acheteur=self.profil_acheteur,
            agriculteur=self.profil_agriculteur,
            statut='en_attente',
            adresse_livraison='Avenue Test, Kinshasa',
            montant_total=Decimal('4500'),
        )
        self.client.login(username='agriculteur', password='Test123!')
        response = self.client.post(reverse('valider_commande', args=[commande.pk]))
        self.assertEqual(response.status_code, 302)
        commande.refresh_from_db()
        self.assertEqual(commande.statut, 'validee')

    def test_refuser_commande_remet_stock(self):
        """Refuser une commande remet le stock à son niveau initial."""
        commande = Commande.objects.create(
            acheteur=self.profil_acheteur,
            agriculteur=self.profil_agriculteur,
            statut='en_attente',
            adresse_livraison='Avenue Test, Kinshasa',
            montant_total=Decimal('4500'),
        )
        LigneCommande.objects.create(
            commande=commande,
            produit=self.produit,
            quantite=10,
            prix_unitaire=Decimal('450'),
            sous_total=Decimal('4500'),
        )
        self.produit.quantite_disponible = 90
        self.produit.save()

        self.client.login(username='agriculteur', password='Test123!')
        self.client.post(reverse('refuser_commande', args=[commande.pk]))

        self.produit.refresh_from_db()
        self.assertEqual(self.produit.quantite_disponible, 100)

    def test_calcul_montant_commande(self):
        """Le montant total est calculé correctement."""
        commande = Commande.objects.create(
            acheteur=self.profil_acheteur,
            agriculteur=self.profil_agriculteur,
            statut='en_attente',
            adresse_livraison='Avenue Test',
            montant_total=Decimal('0'),
        )
        LigneCommande.objects.create(
            commande=commande,
            produit=self.produit,
            quantite=10,
            prix_unitaire=Decimal('450'),
            sous_total=Decimal('4500'),
        )
        total = commande.calculer_montant()
        self.assertEqual(total, Decimal('4500'))

    def test_mes_commandes_acheteur(self):
        """Un acheteur voit uniquement ses propres commandes."""
        Commande.objects.create(
            acheteur=self.profil_acheteur,
            agriculteur=self.profil_agriculteur,
            statut='en_attente',
            adresse_livraison='Avenue Test',
            montant_total=Decimal('4500'),
        )
        self.client.login(username='acheteur', password='Test123!')
        response = self.client.get(reverse('mes_commandes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#1')