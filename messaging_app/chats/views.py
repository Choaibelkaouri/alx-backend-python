from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q   # ← أضف هذا السطر

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Manage conversations.

    A user can see any conversation where:
    - they are in participants OR
    - they have sent at least one message in that conversation
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(
                Q(participants=user) |           # user is a participant
                Q(messages__sender=user)         # OR user sent a message in it
            )
            .distinct()
        )

    def perform_create(self, serializer):
        conversation = serializer.save()
        # ensure the creator is a participant
        conversation.participants.add(self.request.user)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    """
    Manage messages.

    A user can see any message where:
    - they are a participant in the conversation OR
    - they are the sender of that message
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filterset_class = MessageFilter

    def get_queryset(self):
        user = self.request.user
        return (
            Message.objects
            .filter(
                Q(conversation__participants=user) |  # participant in conversation
                Q(sender=user)                        # OR sender of the message
            )
            .select_related('conversation', 'sender')
            .order_by('-created_at')
            .distinct()
        )

    def perform_create(self, serializer):
        """
        When creating a message:
        - make sure the user is a participant (or at least sender)
        - set sender to current user
        """
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)
        serializer.save(sender=self.request.user)
