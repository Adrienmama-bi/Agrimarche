from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import InscriptionForm, ProfilAgriculteurForm, ProfilAcheteurForm, ProfilTransporteurForm, VehiculeForm
from .models import Utilisateur, Vehicule
from assistant.recommandations import get_recommandations



def inscription(request):
    role_initial = request.GET.get('role', 'acheteur')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue sur AgriMarché, {user.first_name} !")
            return redirect('dashboard')
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm(initial={'role': role_initial})
    return render(request, 'accounts/inscription.html', {'form': form, 'role_initial': role_initial})


def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Identifiants incorrects. Réessayez.")
    return render(request, 'accounts/connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('accueil')


@login_required
def dashboard(request):
    user = request.user
    if user.est_agriculteur:
        return redirect('dashboard_agriculteur')
    elif user.est_acheteur:
        return redirect('dashboard_acheteur')
    elif user.est_transporteur:
        return redirect('dashboard_transporteur')
    elif user.est_admin:
        return redirect('dashboard_admin')
    return redirect('accueil')


@login_required
def dashboard_agriculteur(request):
    profil = request.user.profil_agriculteur
    commandes_recentes = profil.commandes_recues.all()[:5]
    produits = profil.produits.all()[:6]
    total_commandes = profil.commandes_recues.count()
    total_produits = profil.produits.filter(statut='actif').count()
    revenus = profil.revenus_total
    return render(request, 'accounts/dashboard_agriculteur.html', {
        'profil': profil,
        'commandes_recentes': commandes_recentes,
        'produits': produits,
        'total_commandes': total_commandes,
        'total_produits': total_produits,
        'revenus': revenus,
    })


@login_required
def dashboard_acheteur(request):
    profil = request.user.profil_acheteur
    commandes_recentes = profil.commandes.all()[:5]
    total_commandes = profil.commandes.count()
    en_livraison = profil.commandes.filter(statut='en_livraison').count()
    recommandations = get_recommandations(profil)
    return render(request, 'accounts/dashboard_acheteur.html', {
        'profil': profil,
        'commandes_recentes': commandes_recentes,
        'total_commandes': total_commandes,
        'en_livraison': en_livraison,
        'recommandations': recommandations,
    })


@login_required
def dashboard_transporteur(request):
    profil = request.user.profil_transporteur
    missions_recentes = profil.livraisons.all()[:5]
    total_missions = profil.livraisons.count()
    missions_actives = profil.livraisons.filter(statut='en_route').count()
    revenus = profil.revenus_total
    return render(request, 'accounts/dashboard_transporteur.html', {
        'profil': profil,
        'missions_recentes': missions_recentes,
        'total_missions': total_missions,
        'missions_actives': missions_actives,
        'revenus': revenus,
    })


@login_required
def dashboard_admin(request):
    if not request.user.est_admin:
        return redirect('accueil')

    from produits.models import Produit
    from commandes.models import Commande
    from livraisons.models import Livraison

    total_users = Utilisateur.objects.count()
    total_produits = Produit.objects.count()
    total_commandes = Commande.objects.count()
    total_livraisons = Livraison.objects.filter(statut__in=['en_route', 'arrivee']).count()
    produits_en_attente = Produit.objects.filter(statut='en_attente').count()
    derniers_users = Utilisateur.objects.order_by('-date_inscription')[:5]
    produits_a_valider = Produit.objects.filter(statut='en_attente').select_related(
        'agriculteur__utilisateur'
    )[:5]

    return render(request, 'accounts/dashboard_admin.html', {
        'total_users': total_users,
        'total_produits': total_produits,
        'total_commandes': total_commandes,
        'total_livraisons': total_livraisons,
        'produits_en_attente': produits_en_attente,
        'derniers_users': derniers_users,
        'produits_a_valider': produits_a_valider,
    })


@login_required
def moderation_produits(request):
    if not request.user.est_admin:
        return redirect('accueil')

    from produits.models import Produit
    statut_filtre = request.GET.get('statut', 'en_attente')
    produits = Produit.objects.select_related('agriculteur__utilisateur', 'categorie')

    if statut_filtre != 'tous':
        produits = produits.filter(statut=statut_filtre)

    return render(request, 'accounts/moderation_produits.html', {
        'produits': produits,
        'statut_filtre': statut_filtre,
    })


@login_required
def valider_produit_admin(request, pk):
    if not request.user.est_admin:
        return redirect('accueil')
    from produits.models import Produit
    produit = get_object_or_404(Produit, pk=pk)
    produit.statut = 'actif'
    produit.save()
    messages.success(request, f"Produit « {produit.nom} » validé et publié.")
    return redirect('moderation_produits')


@login_required
def refuser_produit_admin(request, pk):
    if not request.user.est_admin:
        return redirect('accueil')
    from produits.models import Produit
    produit = get_object_or_404(Produit, pk=pk)
    produit.statut = 'suspendu'
    produit.save()
    messages.success(request, f"Produit « {produit.nom} » refusé.")
    return redirect('moderation_produits')


@login_required
def gestion_utilisateurs(request):
    if not request.user.est_admin:
        return redirect('accueil')

    role_filtre = request.GET.get('role', '')
    users = Utilisateur.objects.all().order_by('-date_inscription')
    if role_filtre:
        users = users.filter(role=role_filtre)

    return render(request, 'accounts/gestion_utilisateurs.html', {
        'users': users,
        'role_filtre': role_filtre,
    })


@login_required
def suspendre_utilisateur(request, pk):
    if not request.user.est_admin:
        return redirect('accueil')
    user = get_object_or_404(Utilisateur, pk=pk)
    user.statut = 'suspendu' if user.statut == 'actif' else 'actif'
    user.save()
    messages.success(request, f"Statut de {user.get_full_name()} mis à jour.")
    return redirect('gestion_utilisateurs')




@login_required
def mon_profil(request):
    user = request.user

    if user.est_agriculteur:
        profil = user.profil_agriculteur
        FormClass = ProfilAgriculteurForm
    elif user.est_acheteur:
        profil = user.profil_acheteur
        FormClass = ProfilAcheteurForm
    elif user.est_transporteur:
        profil = user.profil_transporteur
        FormClass = ProfilTransporteurForm
    else:
        return redirect('dashboard')

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.telephone = form.cleaned_data['telephone']
            if form.cleaned_data.get('photo'):
                user.photo = form.cleaned_data['photo']
            user.save()
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('mon_profil')
    else:
        form = FormClass(instance=profil, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'telephone': user.telephone,
        })

    return render(request, 'accounts/mon_profil.html', {
        'form': form,
        'profil': profil,
    })


@login_required
def gestion_vehicules(request):
    if not request.user.est_transporteur:
        return redirect('accueil')
    profil = request.user.profil_transporteur
    vehicules = profil.vehicules.all()
    return render(request, 'accounts/gestion_vehicules.html', {'vehicules': vehicules})


@login_required
def ajouter_vehicule(request):
    if not request.user.est_transporteur:
        return redirect('accueil')
    profil = request.user.profil_transporteur

    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.transporteur = profil
            vehicule.save()
            messages.success(request, "Véhicule ajouté avec succès.")
            return redirect('gestion_vehicules')
    else:
        form = VehiculeForm()

    return render(request, 'accounts/ajouter_vehicule.html', {'form': form})


@login_required
def supprimer_vehicule(request, pk):
    if not request.user.est_transporteur:
        return redirect('accueil')
    vehicule = get_object_or_404(Vehicule, pk=pk, transporteur=request.user.profil_transporteur)
    if request.method == 'POST':
        vehicule.delete()
        messages.success(request, "Véhicule supprimé.")
        return redirect('gestion_vehicules')
    return redirect('gestion_vehicules')