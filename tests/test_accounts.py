"""
Tests des fonctionnalités d'authentification et gestion des comptes
"""
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Utilisateur, ProfilAgriculteur, ProfilAcheteur, ProfilTransporteur


class TestInscription(TestCase):

    def setUp(self):
        self.client = Client()

    def test_inscription_agriculteur(self):
        """Un agriculteur peut s'inscrire avec ses informations."""
        response = self.client.post(reverse('inscription'), {
            'username': 'agriculteur_test',
            'first_name': 'Jean',
            'last_name': 'Kabila',
            'email': 'jean@test.com',
            'telephone': '+243810000001',
            'role': 'agriculteur',
            'exploitation': 'Ferme Kabila',
            'localisation': 'Kinshasa',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = Utilisateur.objects.get(username='agriculteur_test')
        self.assertEqual(user.role, 'agriculteur')
        self.assertTrue(hasattr(user, 'profil_agriculteur'))
        self.assertEqual(user.profil_agriculteur.exploitation, 'Ferme Kabila')

    def test_inscription_acheteur(self):
        """Un acheteur peut s'inscrire avec son adresse de livraison."""
        response = self.client.post(reverse('inscription'), {
            'username': 'acheteur_test',
            'first_name': 'Marie',
            'last_name': 'Mutombo',
            'email': 'marie@test.com',
            'telephone': '+243810000002',
            'role': 'acheteur',
            'adresse_livraison': 'Avenue de la Paix, Kinshasa',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = Utilisateur.objects.get(username='acheteur_test')
        self.assertEqual(user.role, 'acheteur')
        self.assertTrue(hasattr(user, 'profil_acheteur'))

    def test_inscription_transporteur(self):
        """Un transporteur peut s'inscrire sur la plateforme."""
        response = self.client.post(reverse('inscription'), {
            'username': 'transporteur_test',
            'first_name': 'Pierre',
            'last_name': 'Lumumba',
            'email': 'pierre@test.com',
            'telephone': '+243810000003',
            'role': 'transporteur',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = Utilisateur.objects.get(username='transporteur_test')
        self.assertEqual(user.role, 'transporteur')
        self.assertTrue(hasattr(user, 'profil_transporteur'))

    def test_inscription_mot_de_passe_invalide(self):
        """L'inscription échoue si les mots de passe ne correspondent pas."""
        response = self.client.post(reverse('inscription'), {
            'username': 'user_test',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'telephone': '+243810000004',
            'role': 'acheteur',
            'password1': 'TestPass123!',
            'password2': 'MotDePasseDifferent!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Utilisateur.objects.filter(username='user_test').exists())

    def test_inscription_username_duplique(self):
        """L'inscription échoue si le nom d'utilisateur existe déjà."""
        Utilisateur.objects.create_user(
            username='existant', password='Test123!', role='acheteur'
        )
        response = self.client.post(reverse('inscription'), {
            'username': 'existant',
            'first_name': 'Autre',
            'last_name': 'User',
            'email': 'autre@test.com',
            'telephone': '+243810000005',
            'role': 'acheteur',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Utilisateur.objects.filter(username='existant').count(), 1)


class TestConnexion(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Utilisateur.objects.create_user(
            username='test_user',
            password='TestPass123!',
            role='acheteur',
            first_name='Test',
            last_name='User',
        )
        ProfilAcheteur.objects.create(utilisateur=self.user)

    def test_connexion_valide(self):
        """Un utilisateur peut se connecter avec ses identifiants corrects."""
        response = self.client.post(reverse('connexion'), {
            'username': 'test_user',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_connexion_mot_de_passe_incorrect(self):
        """La connexion échoue avec un mauvais mot de passe."""
        response = self.client.post(reverse('connexion'), {
            'username': 'test_user',
            'password': 'MauvaisMotDePasse!',
        })
        self.assertEqual(response.status_code, 200)

    def test_connexion_utilisateur_inexistant(self):
        """La connexion échoue pour un utilisateur qui n'existe pas."""
        response = self.client.post(reverse('connexion'), {
            'username': 'utilisateur_inexistant',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 200)

    def test_deconnexion(self):
        """Un utilisateur connecté peut se déconnecter."""
        self.client.login(username='test_user', password='TestPass123!')
        response = self.client.get(reverse('deconnexion'))
        self.assertEqual(response.status_code, 302)

    def test_redirection_dashboard_acheteur(self):
        """Un acheteur est redirigé vers son dashboard après connexion."""
        self.client.login(username='test_user', password='TestPass123!')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('dashboard_acheteur'))

    def test_acces_dashboard_sans_connexion(self):
        """Un visiteur non connecté est redirigé vers la connexion."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/connexion/', response.url)


class TestProprietesRole(TestCase):

    def test_propriete_est_agriculteur(self):
        """La propriété est_agriculteur retourne True pour un agriculteur."""
        user = Utilisateur(role='agriculteur')
        self.assertTrue(user.est_agriculteur)
        self.assertFalse(user.est_acheteur)
        self.assertFalse(user.est_transporteur)

    def test_propriete_est_acheteur(self):
        """La propriété est_acheteur retourne True pour un acheteur."""
        user = Utilisateur(role='acheteur')
        self.assertTrue(user.est_acheteur)
        self.assertFalse(user.est_agriculteur)

    def test_propriete_est_transporteur(self):
        """La propriété est_transporteur retourne True pour un transporteur."""
        user = Utilisateur(role='transporteur')
        self.assertTrue(user.est_transporteur)
        self.assertFalse(user.est_acheteur)