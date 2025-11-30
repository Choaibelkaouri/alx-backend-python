from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """Custom manager to work with unread messages only."""

    def get_queryset(self):
        # Base queryset only returns unread messages
        return super().get_queryset().filter(read=False)

    def for_user(self, user):
        """Return unread messages for a specific user, optimized with only()."""
        return (
            self.get_queryset()
            .filter(receiver=user)
            .only("id", "sender", "content", "timestamp")
        )


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        help_text="Parent message if this is a reply in a thread.",
    )

    objects = models.Manager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Notification for {self.user} - message {self.message_id}"


class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history",
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_message_histories",
    )

    class Meta:
        ordering = ["-edited_at"]

    def __str__(self) -> str:
        return f"History for message {self.message_id} at {self.edited_at}"
