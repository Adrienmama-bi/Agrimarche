from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q, Max
from accounts.models import Utilisateur
from .models import Conversation, Message


@login_required
def boite_reception(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        dernier_message=Max('messages__date_envoi')
    ).order_by('-dernier_message')

    return render(request, 'messagerie/boite_reception.html', {
        'conversations': conversations,
    })


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    autre_participant = conversation.participants.exclude(pk=request.user.pk).first()

    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        if contenu:
            Message.objects.create(
                conversation=conversation,
                expediteur=request.user,
                contenu=contenu,
            )
        return redirect('conversation_detail', pk=conversation.pk)

    # Marquer les messages reçus comme lus
    conversation.messages.exclude(expediteur=request.user).update(est_lu=True)

    return render(request, 'messagerie/conversation_detail.html', {
        'conversation': conversation,
        'autre_participant': autre_participant,
        'messages_liste': conversation.messages.all(),
    })


@login_required
def demarrer_conversation(request, utilisateur_id):
    autre_user = get_object_or_404(Utilisateur, pk=utilisateur_id)

    if autre_user == request.user:
        return redirect('boite_reception')

    # Chercher une conversation existante entre les deux
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=autre_user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, autre_user)

    return redirect('conversation_detail', pk=conversation.pk)