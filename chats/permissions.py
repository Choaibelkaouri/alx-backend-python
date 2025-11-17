from rest_framework.permissions import BasePermission
from .models import Conversation, Message

class IsParticipantOfConversation(BasePermission):
    # Custom permission to allow only authenticated users
    # and participants of a conversation to access it or its messages.

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        if isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        return False
