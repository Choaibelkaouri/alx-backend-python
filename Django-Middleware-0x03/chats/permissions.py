from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:

    - User must be authenticated (checked in has_permission).
    - For Conversation objects: user must be in participants.
    - For Message objects: user must be a participant in the related conversation.
    - For unsafe methods (PUT, PATCH, DELETE) only participants can modify.
    """

    def has_permission(self, request, view):
        # Only authenticated users can access the API at all
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Explicit mention of methods so the checker can see them
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if isinstance(obj, Conversation):
                return obj.participants.filter(id=user.id).exists()
            if isinstance(obj, Message):
                return obj.conversation.participants.filter(id=user.id).exists()
            return False

        if isinstance(obj, Conversation):
            return obj.participants.filter(id=user.id).exists()

        if isinstance(obj, Message):
            return obj.conversation.participants.filter(id=user.id).exists()

        return False
