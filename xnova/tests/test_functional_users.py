import json
from django.test.testcases import TestCase
from rest_framework.test import APIClient


class UserRegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def check_for_username_in_response(self, username, response):
        content = response.content.decode()
        root = json.loads(content)
        users = root['data']
        self.assertIn(username, [user['attributes']['name'] for user in users])

    def test_can_register_and_retrieve_it_later(self):
        """
        Ensure we can create a new user.
        """
        url = '/users/'

        # push user
        content = {
            'data': {
                'type': 'users',
                'attributes': {
                    'name': 'NewUser',
                    'email': 'new@example.com',
                    'password': 'password'
                }
            }
        }
        response = self.client.post(url, content, format='json')
        content = response.content.decode()
        root = json.loads(content)
        self.assertEqual(root['data']['attributes']['name'], 'NewUser')

        # register another user
        content = {
            'data': {
                'type': 'users',
                'attributes': {
                    'name': 'AnotherUser',
                    'email': 'another@example.com',
                    'password': 'password'
                }
            }
        }
        self.client.post(url, content, format='json')

        # fetch list
        response = self.client.get(url, format='json')
        self.check_for_username_in_response('NewUser', response)
        self.check_for_username_in_response('AnotherUser', response)
