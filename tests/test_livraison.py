"""
Tests des fonctionnalités de livraison et transport
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Utilisateur, ProfilAgriculteur, ProfilAcheteur, ProfilTransporteur
from produits.models import Produit, Categorie
from commandes.models import Commande
from livraisons.models import Livraison


class TestLivraisons(TestCase):

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

        self.transporteur_user = Utilisateur.objects.create_user(
            username='transporteur', password='Test123!', role='transporteur',
            first_name='Pierre', last_name='Transporteur'
        )
        self.profil_transporteur = ProfilTransporteur.objects.create(
            utilisateur=self.transporteur_user,
            disponible=True,
        )

        self.commande = Commande.objects.create(
            acheteur=self.profil_acheteur,
            agriculteur=self.profil_agriculteur,
            statut='validee',
            adresse_livraison='Avenue Test, Kinshasa',
            montant_total=Decimal('4500'),
        )

        self.livraison = Livraison.objects.create(
            commande=self.commande,
            statut='en_attente',
        )

    def test_missions_visibles_transporteur(self):
        """Un transporteur voit les missions disponibles."""
        self.client.login(username='transporteur', password='Test123!')
        response = self.client.get(reverse('missions_disponibles'))
        self.assertEqual(response.status_code, 200)

    def test_missions_non_visibles_acheteur(self):
        """Un acheteur ne peut pas accéder aux missions."""
        self.client.login(username='acheteur', password='Test123!')
        response = self.client.get(reverse('missions_disponibles'))
        self.assertEqual(response.status_code, 302)

    def test_accepter_mission(self):
        """Un transporteur peut accepter une mission disponible."""
        self.client.login(username='transporteur', password='Test123!')
        response = self.client.post(reverse('accepter_mission', args=[self.livraison.pk]), {
            'distance_km': '12.5',
            'tarif': '5000',
        })
        self.assertEqual(response.status_code, 302)
        self.livraison.refresh_from_db()
        self.assertEqual(self.livraison.statut, 'assignee')
        self.assertEqual(self.livraison.transporteur, self.profil_transporteur)

    def test_statut_commande_mis_a_jour_apres_acceptation(self):
        """La commande passe en livraison quand le transporteur accepte."""
        self.client.login(username='transporteur', password='Test123!')
        self.client.post(reverse('accepter_mission', args=[self.livraison.pk]), {
            'distance_km': '12.5',
            'tarif': '5000',
        })
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, 'en_livraison')

    def test_mettre_a_jour_statut_en_route(self):
        """Le transporteur peut mettre la livraison en route."""
        self.livraison.transporteur = self.profil_transporteur
        self.livraison.statut = 'assignee'
        self.livraison.save()

        self.client.login(username='transporteur', password='Test123!')
        response = self.client.post(
            reverse('mettre_a_jour_statut', args=[self.livraison.pk, 'en_route'])
        )
        self.assertEqual(response.status_code, 302)
        self.livraison.refresh_from_db()
        self.assertEqual(self.livraison.statut, 'en_route')

    def test_statut_invalide_refuse(self):
        """Un statut invalide est refusé."""
        self.livraison.transporteur = self.profil_transporteur
        self.livraison.statut = 'assignee'
        self.livraison.save()

        self.client.login(username='transporteur', password='Test123!')
        response = self.client.post(
            reverse('mettre_a_jour_statut', args=[self.livraison.pk, 'statut_inventé'])
        )
        self.livraison.refresh_from_db()
        self.assertEqual(self.livraison.statut, 'assignee')

    def test_creation_livraison_apres_validation_commande(self):
        """Une livraison est créée automatiquement quand l'agriculteur valide."""
        nouvelle_commande = Commande.objects.create(
            acheteur=self.profil_acheteur,
            agriculteur=self.profil_agriculteur,
            statut='en_attente',
            adresse_livraison='Avenue Test',
            montant_total=Decimal('2000'),
        )
        self.client.login(username='agriculteur', password='Test123!')
        self.client.post(reverse('valider_commande', args=[nouvelle_commande.pk]))
        self.assertTrue(Livraison.objects.filter(commande=nouvelle_commande).exists())