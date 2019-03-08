import os
from io import BytesIO

import msgpack
from django.contrib.auth.models import User, Group
from django.test import TestCase, RequestFactory, Client
import requests
from rest_framework.test import APIRequestFactory, APIClient

from backend.api.models import GameVersion


class AuthTest(TestCase):
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
        self.assertEqual(self.client.get('/api/user/').data.get('username'), 'test')


class APITest(TestCase):
    def setUp(self):
        self.client = Client()
        u = User.objects.create_user(username='test', password='test', is_superuser=True)
        # g = Group.objects.get(name='standard_user')
        # u.groups.set([g])
        # u.save()
        self.game_version = GameVersion.objects.create(name='base')
        self.client.post('/login', {'username': 'test', 'password': 'test'})

    def test_status(self):
        self.assertEqual(self.client.get('/api/status/').data.get('users'), 1)

    def test_imperium_create_by_uuid(self):
        # wrong
        data = {
            "name": "settings",
            "type_id": 5,  # settings == 6
            "game_version": self.game_version.id,
            "uuid": '38c0f024-affc-41ce-b9fc-61a3c7680b65'
        }
        self.assertEqual(self.client.post('/api/imperium/', data).status_code, 400)
        # right
        data['type_id'] = 6
        imperium_id = self.client.post('/api/imperium/', data).data.get('id')
        # test unpack
        imperium_unpacked = self.client.get('/api/imperium/%s/unpack/' % imperium_id).data
        self.assertTrue(isinstance(imperium_unpacked['C']['Config'], dict))
        # duplicate
        self.assertEqual(self.client.post('/api/imperium/', data).status_code, 400)

    def test_imperium_create_by_upload(self):
        data = {
            "name": "settings",
            "type_id": 6,  # settings == 6
            "game_version": self.game_version.id,
            "upload_file": None
        }
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testcase', 'imperium_upload'), 'rb') as f:
            data['upload_file'] = f
            imperium_id = self.client.post('/api/imperium/', data).data.get('id')
            # test unpack
            imperium_unpacked = self.client.get('/api/imperium/%s/unpack/' % imperium_id).data
            # print(imperium_unpacked['C']['Config'])
            self.assertTrue(isinstance(imperium_unpacked['C']['Config'], dict))
        # ImperiumHandleError
        data['upload_file'] = BytesIO(b'0x62')
        self.assertEqual(self.client.post('/api/imperium/', data).status_code, 400)

    def test_imperium_diff(self):
        # upload diff data
        old = msgpack.dumps({'C': {'test': {'K': ['name'], 'D': [['Puggi']], 'T': ['String']}}})
        new = msgpack.dumps({'C': {'test': {'K': ['name'], 'D': [['Puggii']], 'T': ['String']}}})
        old_id = self.client.post('/api/imperium/', {
            "name": "settings",
            "type_id": 6,  # settings == 6
            "game_version": self.game_version.id,
            "upload_file": BytesIO(old)
        }).data.get('id')
        new_id = self.client.post('/api/imperium/', {
            "name": "settings",
            "type_id": 6,  # settings == 6
            "game_version": self.game_version.id,
            "upload_file": BytesIO(new)
        }).data.get('id')
        # print(old_id,new_id)
        # 2 diff
        self.assertEqual(
            len(self.client.get('/api/imperium/diff/', {'old': old_id, 'new': new_id}).data['C']['test']['D']), 2)
        self.assertIn("-'Puggi'$0\n+'Puggii'$0",
                      self.client.get('/api/imperium/diff_text/', {'old': old_id, 'new': new_id}).data)
