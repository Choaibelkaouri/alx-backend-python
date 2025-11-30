from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Message, Notification, MessageHistory

User = get_user_model()


class MessagingSignalsTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="test12345")
        self.receiver = User.objects.create_user(username="receiver", password="test12345")

    def test_notification_created_on_new_message(self):
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello there!",
        )
        self.assertTrue(
            Notification.objects.filter(user=self.receiver, message=msg).exists()
        )

    def test_message_history_created_on_edit(self):
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original",
        )
        msg.content = "Edited"
        msg.save()

        histories = MessageHistory.objects.filter(message=msg)
        self.assertEqual(histories.count(), 1)
        self.assertEqual(histories.first().old_content, "Original")

    def test_unread_manager_for_user(self):
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread",
        )
        unread_for_receiver = Message.unread.for_user(self.receiver)
        self.assertEqual(unread_for_receiver.count(), 1)
