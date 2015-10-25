import json
from django.test.testcases import TestCase
from rest_framework.test import APIClient


class PlayerRegisterTest(TestCase):
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
        url = '/players/'

        # push user
        content = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'NewPlayer',
                    'email': 'new@example.com',
                    'password': 'password'
                }
            }
        }
        response = self.client.post(url, content, format='json')
        content = response.content.decode()
        root = json.loads(content)
        self.assertEqual(root['data']['attributes']['name'], 'NewPlayer')

        # register another user
        content = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'AnotherPlayer',
                    'email': 'another@example.com',
                    'password': 'password'
                }
            }
        }
        self.client.post(url, content, format='json')

        # fetch list
        response = self.client.get(url, format='json')
        self.check_for_username_in_response('NewPlayer', response)
        self.check_for_username_in_response('AnotherPlayer', response)

    def test_cannot_register_same_name_players(self):
        url = '/players/'
        content = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'AwesomeName',
                    'email': 'awesome@example.com',
                    'password': 'password'
                }
            }
        }
        self.client.post(url, content, format='json')
        content['data']['attributes']['email'] = 'another@email.com'
        response = self.client.post(url, content, format='json')
        content = response.content.decode()
        root = json.loads(content)
        # self.assertEqual(root['errors'][0]['status'], '422')
        self.assertEqual(
            root['errors'][0]['detail'],
            'A user with the same name already exists')
        self.assertEqual(
            root['errors'][0]['source'],
            {'pointer': '/data/attributes/name'})
