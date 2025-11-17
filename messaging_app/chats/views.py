from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.

    - Users must be authenticated.
    - Each user can only see conversations where they are a participant.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        user = self.request.user
        # Only conversations the user participates in
        return Conversation.objects.filter(participants=user).distinct()

    def perform_create(self, serializer):
        # When a conversation is created, add the current user as a participant.
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.

    - Users must be authenticated.
    - Each user can only see messages in conversations where they are a participant.
    - Pagination: 20 messages per page.
    - Filtering is enabled via MessageFilter.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filterset_class = MessageFilter

    def get_queryset(self):
        user = self.request.user
        # Only messages from conversations the user participates in
        return (
            Message.objects
            .filter(conversation__participants=user)
            .select_related('conversation', 'sender')
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        """
        When creating a message:
        - Ensure the current user is a participant in the conversation.
        - Set the sender to the current user.
        """
        conversation = serializer.validated_data['conversation']
        from rest_framework.exceptions import PermissionDenied

        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant of this conversation.")

        serializer.save(sender=self.request.user)
