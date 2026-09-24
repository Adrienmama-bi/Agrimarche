"""
Tests du moteur IA local (chatbot, recommandations, modération)
"""
from decimal import Decimal
from django.test import TestCase
from accounts.models import Utilisateur, ProfilAgriculteur, ProfilAcheteur
from produits.models import Produit, Categorie
from assistant.ia_engine import repondre_chatbot, calculer_recommandations, analyser_produit_local


class TestChatbot(TestCase):

    def test_reponse_salutation(self):
        """Le chatbot répond à une salutation."""
        reponse = repondre_chatbot("Bonjour")
        self.assertIsInstance(reponse, str)
        self.assertGreater(len(reponse), 0)

    def test_reponse_inscription(self):
        """Le chatbot répond à une question sur l'inscription."""
        reponse = repondre_chatbot("Comment je peux m'inscrire ?")
        self.assertIsInstance(reponse, str)
        self.assertGreater(len(reponse), 10)

    def test_reponse_commande(self):
        """Le chatbot répond à une question sur les commandes."""
        reponse = repondre_chatbot("Comment passer une commande ?")
        self.assertIn('commande', reponse.lower())

    def test_reponse_paiement(self):
        """Le chatbot répond à une question sur le paiement."""
        reponse = repondre_chatbot("Quels sont les modes de paiement ?")
        self.assertIn('mobile money', reponse.lower())

    def test_reponse_livraison(self):
        """Le chatbot répond à une question sur la livraison."""
        reponse = repondre_chatbot("Où est ma livraison ?")
        self.assertIsInstance(reponse, str)
        self.assertGreater(len(reponse), 10)

    def test_reponse_question_inconnue(self):
        """Le chatbot gère les questions hors sujet avec une réponse par défaut."""
        reponse = repondre_chatbot("Quel est le temps qu'il fait aujourd'hui ?")
        self.assertIsInstance(reponse, str)
        self.assertGreater(len(reponse), 0)

    def test_reponse_avec_role_agriculteur(self):
        """Le chatbot personnalise sa réponse selon le rôle agriculteur."""
        reponse = repondre_chatbot("Je ne comprends rien", role_utilisateur='agriculteur')
        self.assertIn('agriculteur', reponse.lower())

    def test_reponse_avec_role_acheteur(self):
        """Le chatbot personnalise sa réponse selon le rôle acheteur."""
        reponse = repondre_chatbot("Je ne comprends rien", role_utilisateur='acheteur')
        self.assertIn('acheteur', reponse.lower())

    def test_reponse_merci(self):
        """Le chatbot répond aux remerciements."""
        reponse = repondre_chatbot("Merci beaucoup")
        self.assertIsInstance(reponse, str)
        self.assertGreater(len(reponse), 5)


class TestModeration(TestCase):

    def setUp(self):
        self.agriculteur_user = Utilisateur.objects.create_user(
            username='agri', password='Test123!', role='agriculteur'
        )
        self.profil_agriculteur = ProfilAgriculteur.objects.create(
            utilisateur=self.agriculteur_user,
            exploitation='Ferme Test',
            localisation='Kinshasa',
        )
        self.categorie = Categorie.objects.create(nom='Céréales', icone='🌽')

    def _creer_produit(self, **kwargs):
        defaults = {
            'agriculteur': self.profil_agriculteur,
            'categorie': self.categorie,
            'nom': 'Maïs frais',
            'description': 'Du maïs frais de très bonne qualité récolté ce matin',
            'prix_unitaire': Decimal('450'),
            'unite': 'kg',
            'quantite_disponible': 100,
            'statut': 'en_attente',
        }
        defaults.update(kwargs)
        return Produit.objects.create(**defaults)

    def test_produit_conforme(self):
        """Un produit complet et cohérent est marqué conforme."""
        produit = self._creer_produit()
        statut, raison = analyser_produit_local(produit)
        self.assertEqual(statut, 'conforme')

    def test_produit_description_trop_courte(self):
        """Un produit avec une description trop courte est marqué à vérifier."""
        produit = self._creer_produit(description='Court')
        statut, raison = analyser_produit_local(produit)
        self.assertIn(statut, ['a_verifier', 'non_conforme'])

    def test_produit_prix_zero(self):
        """Un produit avec un prix à zéro est non conforme."""
        produit = self._creer_produit(prix_unitaire=Decimal('0'))
        statut, raison = analyser_produit_local(produit)
        self.assertEqual(statut, 'non_conforme')

    def test_produit_prix_suspect(self):
        """Un produit avec un prix anormalement bas est marqué à vérifier."""
        produit = self._creer_produit(prix_unitaire=Decimal('1'))
        statut, raison = analyser_produit_local(produit)
        self.assertIn(statut, ['a_verifier', 'non_conforme'])

    def test_produit_mot_interdit(self):
        """Un produit contenant un mot interdit est non conforme."""
        produit = self._creer_produit(
            nom='Drogue qualité supérieure',
            description='Description longue avec mot interdit drogue disponible'
        )
        statut, raison = analyser_produit_local(produit)
        self.assertEqual(statut, 'non_conforme')

    def test_produit_nom_trop_court(self):
        """Un produit avec un nom trop court est non conforme."""
        produit = self._creer_produit(nom='AB')
        statut, raison = analyser_produit_local(produit)
        self.assertEqual(statut, 'non_conforme')

    def test_produit_stock_nul(self):
        """Un produit avec un stock nul est marqué à vérifier."""
        produit = self._creer_produit(quantite_disponible=0)
        statut, raison = analyser_produit_local(produit)
        self.assertIn(statut, ['a_verifier', 'non_conforme'])

    def test_raison_toujours_presente(self):
        """Chaque analyse fournit toujours une raison."""
        produit = self._creer_produit()
        statut, raison = analyser_produit_local(produit)
        self.assertIsInstance(raison, str)
        self.assertGreater(len(raison), 0)


class TestRecommandations(TestCase):

    def setUp(self):
        self.agriculteur_user = Utilisateur.objects.create_user(
            username='agri', password='Test123!', role='agriculteur'
        )
        self.profil_agriculteur = ProfilAgriculteur.objects.create(
            utilisateur=self.agriculteur_user,
            exploitation='Ferme Test',
            localisation='Kinshasa',
        )
        self.acheteur_user = Utilisateur.objects.create_user(
            username='acheteur', password='Test123!', role='acheteur'
        )
        self.profil_acheteur = ProfilAcheteur.objects.create(
            utilisateur=self.acheteur_user,
            adresse_livraison='Avenue Test'
        )
        self.categorie = Categorie.objects.create(nom='Céréales', icone='🌽')

    def _creer_produit(self, nom, prix=450):
        return Produit.objects.create(
            agriculteur=self.profil_agriculteur,
            categorie=self.categorie,
            nom=nom,
            description='Description suffisamment longue pour le test',
            prix_unitaire=Decimal(str(prix)),
            unite='kg',
            quantite_disponible=100,
            statut='actif',
        )

    def test_recommandations_sans_historique(self):
        """Des recommandations sont générées même sans historique d'achats."""
        produit1 = self._creer_produit('Maïs frais')
        produit2 = self._creer_produit('Manioc')
        produit3 = self._creer_produit('Haricot')

        produits = Produit.objects.filter(statut='actif')
        resultats = calculer_recommandations(self.profil_acheteur, produits, limite=3)
        self.assertGreater(len(resultats), 0)

    def test_recommandations_retourne_tuple(self):
        """Chaque recommandation retourne un tuple (produit, raison)."""
        self._creer_produit('Maïs frais')
        produits = Produit.objects.filter(statut='actif')
        resultats = calculer_recommandations(self.profil_acheteur, produits, limite=3)
        for item in resultats:
            self.assertEqual(len(item), 2)
            produit, raison = item
            self.assertIsInstance(produit, Produit)
            self.assertIsInstance(raison, str)

    def test_recommandations_limite_respectee(self):
        """Le nombre de recommandations respecte la limite demandée."""
        for i in range(10):
            self._creer_produit(f'Produit {i}')
        produits = Produit.objects.filter(statut='actif')
        resultats = calculer_recommandations(self.profil_acheteur, produits, limite=4)
        self.assertLessEqual(len(resultats), 4)

    def test_raison_non_vide(self):
        """Chaque recommandation a une raison non vide."""
        self._creer_produit('Maïs frais')
        produits = Produit.objects.filter(statut='actif')
        resultats = calculer_recommandations(self.profil_acheteur, produits, limite=3)
        for produit, raison in resultats:
            self.assertGreater(len(raison), 0)