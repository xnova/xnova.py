import json
from django.test.testcases import TestCase
from rest_framework.test import APIClient


class PlayerRegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def request_create_player(self, name, email, password):
        return self.client.post('/players/', {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': name,
                    'email': email,
                    'password': password
                }
            }
        }, format='json')

    def check_for_username_in_response(self, username, response):
        content = response.content.decode()
        root = json.loads(content)
        users = root['data']
        self.assertIn(username, [user['attributes']['name'] for user in users])

    def test_can_register_and_retrieve_it_later(self):
        """
        Ensure we can create a new user.
        """

        # push player
        response = self.request_create_player(
            'NewPlayer', 'new@example.com', 'password')
        content = response.content.decode()
        root = json.loads(content)
        self.assertEqual(root['data']['attributes']['name'], 'NewPlayer')

        # register another player
        self.request_create_player(
            'AnotherPlayer', 'another@example.com', 'password')

        # fetch list
        response = self.client.get('/players/', format='json')
        self.check_for_username_in_response('NewPlayer', response)
        self.check_for_username_in_response('AnotherPlayer', response)

    def test_cannot_register_same_name_players(self):
        self.request_create_player('AwesomeName', 'awesome@example.com',
                                   'password')
        response = self.request_create_player(
            'AwesomeName', 'another@example.com', 'password')
        content = response.content.decode()
        root = json.loads(content)
        # self.assertEqual(root['errors'][0]['status'], '422')
        self.assertEqual(
            root['errors'][0]['detail'],
            'A player with the same name already exists')
        self.assertEqual(
            root['errors'][0]['source'],
            {'pointer': '/data/attributes/name'})

    def test_cannot_register_same_email_players(self):
        self.request_create_player('PlayerA', 'admin@example.com', 'password')
        response = self.request_create_player('PlayerB', 'admin@example.com',
                                              'password')
        content = response.content.decode()
        root = json.loads(content)
        self.assertEqual(
            root['errors'][0]['detail'],
            'A player with the same email already exists')
        self.assertEqual(
            root['errors'][0]['source'],
            {'pointer': '/data/attributes/email'})
