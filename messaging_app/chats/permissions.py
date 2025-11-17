from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:

    - User must be authenticated (handled by default permission classes).
    - For Conversation objects: user must be in participants.
    - For Message objects: user must be a participant in the related conversation.
    """

    def has_permission(self, request, view):
        # Only authenticated users can access the API
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, Conversation):
            # User must be in the participants of the conversation
            return obj.participants.filter(id=user.id).exists()

        if isinstance(obj, Message):
            # User must be a participant of the message's conversation
            return obj.conversation.participants.filter(id=user.id).exists()

        return False
