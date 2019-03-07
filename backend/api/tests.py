import os

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory, Client
import requests
from rest_framework.test import APIRequestFactory, APIClient


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.client = Client()
        User.objects.create_user(username='test', password='test')

    def get_index(self):
        return self.client.get('/', follow=True).content

    def test_password_auth(self):
        self.assertEqual(self.client.get('/api/').status_code, 403)
        self.assertTrue(b'Signin' in self.get_index())
        # wrong
        r = self.client.post('/login', {'username': 'test', 'password': '123'})
        self.assertTrue(b'Invalid' in r.content)
        # right
        self.client.post('/login', {'username': 'test', 'password': 'test'})
        self.assertTrue(b'django-vue' in self.get_index())

    def test_user_info(self):
        self.client.post('/login', {'username': 'test', 'password': 'test'})
        self.assertTrue(b'django-vue' in self.get_index())
        self.assertEqual(self.client.get('/api/user/').data.get('username'),'test')