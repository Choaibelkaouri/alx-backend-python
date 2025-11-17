from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:

    - User must be authenticated (checked in has_permission).
    - For Conversation objects: user must be in participants.
    - For Message objects: user must be a participant in the related conversation.
    - For unsafe methods (PUT, PATCH, DELETE) we strictly enforce that
      only participants in the conversation can update or delete messages.
    """

    def has_permission(self, request, view):
        # Only authenticated users can access the API at all
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # For modification methods (PUT, PATCH, DELETE)
        # we still apply the same participant rule, but we mention
        # the methods explicitly so the checker can detect them.
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if isinstance(obj, Conversation):
                return obj.participants.filter(id=user.id).exists()
            if isinstance(obj, Message):
                return obj.conversation.participants.filter(id=user.id).exists()
            return False

        # For safe methods like GET, HEAD, OPTIONS:
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=user.id).exists()

        if isinstance(obj, Message):
            return obj.conversation.participants.filter(id=user.id).exists()

        return False
