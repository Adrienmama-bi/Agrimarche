from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('produits.urls')),
    path('accounts/', include('accounts.urls')),
    path('produits/', include('produits.urls')),
    path('commandes/', include('commandes.urls')),
    path('livraisons/', include('livraisons.urls')),
    path('paiements/', include('paiements.urls')),
    path('messagerie/', include('messagerie.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('accounts.dashboard_urls')),
    path('assistant/', include('assistant.urls')),
    path('hors-ligne/', TemplateView.as_view(template_name='pwa/hors_ligne.html'), name='hors_ligne'),
    path('manifest.json', TemplateView.as_view(
        template_name='pwa/manifest.json',
        content_type='application/manifest+json',
    ), name='manifest'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)