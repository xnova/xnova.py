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
        self.assertIn(username, [user.name for user in users])

    def test_can_register_and_retrieve_it_later(self):
        """
        Ensure we can create a new user.
        """
        url = '/users/'

        # push user
        content = {
            'data': {
                'name': 'NewUser',
                'email': 'new@example.com',
                'password': 'password'
            }
        }
        self.client.post(url, content, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response['content-type'], 'application/vnd.api+json')

        # fetch list
        response = self.client.get(url, format='json')
        self.check_for_username_in_response('NewUser', response)

        # register another user
        content = {
            'data': {
                'name': 'AnotherUser',
                'email': 'another@example.com',
                'password': 'password'
            }
        }
        self.client.post(url, content, format='json')

        # fetch list
        response = self.client.get(url, format='json')
        self.check_for_username_in_response('NewUser', response)
        self.check_for_username_in_response('AnotherUser', response)
