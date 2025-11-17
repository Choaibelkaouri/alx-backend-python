from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination

class ConversationViewSet(viewsets.ModelViewSet):
    # ViewSet for managing conversations.
    # Only conversations where the current user is a participant are visible.
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).distinct()

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()

class MessageViewSet(viewsets.ModelViewSet):
    # ViewSet for managing messages.
    # Only messages from conversations where the user is a participant are visible.
    # Supports pagination and filtering.
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filterset_class = MessageFilter

    def get_queryset(self):
        user = self.request.user
        return (
            Message.objects
            .filter(conversation__participants=user)
            .select_related('conversation', 'sender')
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        # When creating a message, automatically set the sender as the current user.
        # Also ensure the user is a participant of the conversation.
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You are not a participant of this conversation.')
        serializer.save(sender=self.request.user)
