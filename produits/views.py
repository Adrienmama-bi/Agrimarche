from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Categorie, PhotoProduit
from .forms import ProduitForm


def accueil(request):
    produits_recents = (
        Produit.objects.filter(statut='actif')
        .select_related('agriculteur__utilisateur')
        .prefetch_related('photos')[:6]
    )
    categories = Categorie.objects.all()[:8]

    recommandations = []
    if request.user.is_authenticated and request.user.est_acheteur:
        from assistant.recommandations import get_recommandations
        recommandations = get_recommandations(request.user.profil_acheteur, limite=4)

    return render(request, 'produits/accueil.html', {
        'produits_recents': produits_recents,
        'categories': categories,
        'recommandations': recommandations,
    })


def catalogue(request):
    produits = Produit.objects.filter(statut='actif').select_related(
        'agriculteur__utilisateur', 'categorie'
    ).prefetch_related('photos')

    categorie_id = request.GET.get('categorie')
    recherche = request.GET.get('q', '').strip()
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    bio = request.GET.get('bio')

    if categorie_id:
        produits = produits.filter(categorie__id=categorie_id)
    if recherche:
        produits = produits.filter(nom__icontains=recherche)
    if prix_min:
        produits = produits.filter(prix_unitaire__gte=prix_min)
    if prix_max:
        produits = produits.filter(prix_unitaire__lte=prix_max)
    if bio:
        produits = produits.filter(est_bio=True)

    categories = Categorie.objects.all()

    return render(request, 'produits/catalogue.html', {
        'produits': produits,
        'categories': categories,
        'recherche': recherche,
        'categorie_id': categorie_id,
        'total': produits.count(),
    })


def detail_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk, statut='actif')
    produit.nombre_vues += 1
    produit.save()
    autres_produits = Produit.objects.filter(
        agriculteur=produit.agriculteur,
        statut='actif'
    ).exclude(pk=pk)[:3]
    return render(request, 'produits/detail_produit.html', {
        'produit': produit,
        'autres_produits': autres_produits,
    })


@login_required
def publier_produit(request):
    if not request.user.est_agriculteur:
        messages.error(request, "Accès réservé aux agriculteurs.")
        return redirect('accueil')

    profil = request.user.profil_agriculteur

    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.agriculteur = profil
            produit.statut = 'en_attente'
            produit.save()

            # Photos multiples
            photos = request.FILES.getlist('photos')
            for i, photo in enumerate(photos):
                PhotoProduit.objects.create(
                    produit=produit,
                    image=photo,
                    est_principale=(i == 0),
                    ordre=i
                )

            messages.success(request, "Votre produit a été soumis et est en attente de validation.")
            return redirect('dashboard_agriculteur')
        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ProduitForm(initial={'localisation': profil.localisation})

    return render(request, 'produits/publier_produit.html', {'form': form})


@login_required
def mes_produits(request):
    if not request.user.est_agriculteur:
        return redirect('accueil')
    profil = request.user.profil_agriculteur
    produits = profil.produits.all().prefetch_related('photos')
    return render(request, 'produits/mes_produits.html', {'produits': produits})


@login_required
def modifier_produit(request, pk):
    if not request.user.est_agriculteur:
        return redirect('accueil')
    profil = request.user.profil_agriculteur
    produit = get_object_or_404(Produit, pk=pk, agriculteur=profil)

    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            photos = request.FILES.getlist('photos')
            for i, photo in enumerate(photos):
                PhotoProduit.objects.create(
                    produit=produit,
                    image=photo,
                    ordre=produit.photos.count() + i
                )
            messages.success(request, "Produit mis à jour avec succès.")
            return redirect('mes_produits')
    else:
        form = ProduitForm(instance=produit)

    return render(request, 'produits/modifier_produit.html', {
        'form': form,
        'produit': produit,
    })


@login_required
def supprimer_produit(request, pk):
    if not request.user.est_agriculteur:
        return redirect('accueil')
    produit = get_object_or_404(Produit, pk=pk, agriculteur=request.user.profil_agriculteur)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, "Produit supprimé.")
        return redirect('mes_produits')
    return render(request, 'produits/confirmer_suppression.html', {'produit': produit})