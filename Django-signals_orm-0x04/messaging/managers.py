from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to work with unread messages.
    """

    def get_queryset(self):
        # Base queryset: unread messages only
        return super().get_queryset().filter(read=False)

    def unread_for_user(self, user):
        """
        Return unread messages for a specific user.
        """
        return self.get_queryset().filter(receiver=user)
