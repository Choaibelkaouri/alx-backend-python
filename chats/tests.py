from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Conversation

User = get_user_model()

class ConversationAPITestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_create_conversation(self):
        response = self.client.post('/api/conversations/', {})
        self.assertEqual(response.status_code, 201)
