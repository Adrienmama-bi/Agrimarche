from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'destinataire', 'type_notif', 'canal', 'est_lue', 'date_envoi']
    list_filter = ['type_notif', 'canal', 'est_lue']
    search_fields = ['titre', 'destinataire__username']