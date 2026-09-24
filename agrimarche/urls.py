from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)