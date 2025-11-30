from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Message, Notification, MessageHistory

User = get_user_model()


@receiver(post_save, sender=Message)
def create_notification_for_new_message(sender, instance, created, **kwargs):
    """Create a notification whenever a new message is created."""
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edits(sender, instance, **kwargs):
    """Before saving an edited message, store the old content in MessageHistory."""
    # Only run on updates (existing messages)
    if not instance.pk:
        return

    try:
        old_instance = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    # If content changed, store old content in history and mark as edited
    if old_instance.content != instance.content:
        MessageHistory.objects.create(
            message=old_instance,
            old_content=old_instance.content,
            edited_by=instance.sender,
        )
        instance.edited = True


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """Delete messages, notifications, and message histories of a deleted user.

    We still keep this logic explicit even if on_delete behavior already
    cascades some of it, to match project requirements.
    """
    # Delete messages where the user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete notifications for the user
    Notification.objects.filter(user=instance).delete()

    # Delete histories they created as editor
    MessageHistory.objects.filter(edited_by=instance).delete()
