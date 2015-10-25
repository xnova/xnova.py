import json

from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APITestCase
from xnova.views import player_list, player_detail


class PlayerListTest(APITestCase):
    def test_players_url_resolves_to_player_list_view(self):
        found = resolve('/players/')
        self.assertEqual(found.func, player_list)

    def check_is_valid_jsonapi(self, response):
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

        content = response.content.decode()

        root = json.loads(content)
        self.assertIsInstance(root, dict)
        self.assertTrue('data' in root or 'errors' in root or 'meta' in root)
        valid_members = ('data', 'errors', 'meta', 'jsonapi', 'links',
                         'included')
        for member in root:
            self.assertIn(member, valid_members)

        if 'data' not in root:
            self.assertNotIn('included', root,
                             "If a document does not contain a top-level data "
                             "key, the included member MUST NOT be present "
                             "either.")
        elif isinstance(root['data'], dict):
            if 'links' in root['data'].keys():
                self.assertIsInstance(root['data']['links'], dict)

        if 'errors' in root:
            self.assertTrue(400 <= response.status_code < 600)
            self.assertIsInstance(root['errors'], list)
            self.assertGreater(len(root['errors']), 0)
            for error in root['errors']:
                self.assertIsInstance(error, dict)

    # TODO
    # jsonapi.org
    def test_returns_valid_jsonapi(self):
        response = self.client.get('/players/', format='json')
        self.check_is_valid_jsonapi(response)

    def test_can_save_a_POST_request(self):
        response = self.client.post('/players/', {
            'data': {
                'type': 'users',
                'attributes': {
                    'name': 'PostUser',
                    'email': 'post@example.com',
                    'password': 'password'
                }
            }
        }, format='json')

        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.all()[0]  # .first() doesnt work in django1.5
        self.assertEqual(new_user.username, 'PostUser')
        self.assertEqual(new_user.email, 'post@example.com')

        content = response.content.decode()
        root = json.loads(content)
        attributes = root['data']['attributes']
        self.assertEqual('PostUser', attributes['name'])
        self.assertEqual('post@example.com', attributes['email'])

    def test_returns_data_array(self):
        response = self.client.get('/players/', format='json')

        content = response.content.decode()
        root = json.loads(content)
        self.assertIn('data', root.keys())
        self.assertIsInstance(root['data'], list)

    def test_displays_all_players_attributes(self):
        User.objects.create_user('Alice', email='alice@example.com')
        User.objects.create_user('Bob', email='bob@example.com')

        response = self.client.get('/players/', format='json')
        root = json.loads(response.content.decode())

        self.assertEqual({
            'name': 'Alice',
            'email': 'alice@example.com'
        }, root['data'][0]['attributes'])
        self.assertEqual({
            'name': 'Bob',
            'email': 'bob@example.com'
        }, root['data'][1]['attributes'])
        self.assertIn('links', root['data'][0].keys())
        self.assertIn('links', root['data'][1].keys())
        self.assertIsInstance(root['data'][0]['links'], dict)
        self.assertIsInstance(root['data'][1]['links'], dict)
        self.assertIn('self', root['data'][0]['links'].keys())
        self.assertIn('self', root['data'][1]['links'].keys())
        self.assertNotEqual(root['data'][0]['links']['self'],
                            root['data'][1]['links']['self'])

    def test_doesnt_throw_exception_unique_username(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'PostUser',
                    'email': 'post@example.com',
                    'password': 'password'
                }
            }
        }
        try:
            self.client.post('/players/', data, format='json')
            data['data']['attributes']['email'] = 'other@mail.com'
            self.client.post('/players/', data, format='json')
        except IntegrityError, e:
            self.assertNotIn('auth_user.username', e.message)

    def test_returns_valid_jsonapi_when_same_username(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'MultiPlayer',
                    'email': 'post@example.com',
                    'password': 'password'
                }
            }
        }
        self.client.post('/players/', data, format='json')
        data['data']['attributes']['email'] = 'another@email.com'
        response = self.client.post('/players/', data, format='json')
        self.check_is_valid_jsonapi(response)

    def test_returns_errors_when_same_username(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'MultiPlayer',
                    'email': 'post@example.com',
                    'password': 'password'
                }
            }
        }
        self.client.post('/players/', data, format='json')
        data['data']['attributes']['email'] = 'another@email.com'
        response = self.client.post('/players/', data, format='json')
        content = response.content.decode()
        root = json.loads(content)
        self.assertIn('errors', root.keys())
        self.assertEqual(
            root['errors'][0]['source'],
            {'pointer': '/data/attributes/name'}
        )
        self.assertEqual(
            root['errors'][0]['detail'],
            'A player with the same name already exists'
        )

    def test_returns_valid_jsonapi_when_same_email(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'APlayer',
                    'email': 'incredible@email.com',
                    'password': 'password'
                }
            }
        }
        self.client.post('/players/', data, format='json')
        data['data']['attributes']['name'] = 'AnotherPlayer'
        response = self.client.post('/players/', data, format='json')
        self.check_is_valid_jsonapi(response)

    def test_returns_errors_when_same_email(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'Alice',
                    'email': 'awesome@mail.com',
                    'password': 'password'
                }
            }
        }
        response = self.client.post('/players/', data, format='json')
        content = response.content.decode()
        root = json.loads(content)
        self.assertIn('data', root.keys())
        data['data']['attributes']['name'] = 'Bob'
        response = self.client.post('/players/', data, format='json')
        content = response.content.decode()
        root = json.loads(content)
        self.assertIn('errors', root.keys())
        self.assertEqual(
            root['errors'][0]['detail'],
            'A player with the same email already exists'
        )
        self.assertEqual(
            root['errors'][0]['source'],
            {'pointer': '/data/attributes/email'}
        )

    def test_return_valid_jsonapi_after_creating(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'APlayer',
                    'email': 'normal@email.com',
                    'password': 'password'
                }
            }
        }
        response = self.client.post('/players/', data, format='json')
        self.check_is_valid_jsonapi(response)

    def test_return_self_link_after_creating(self):
        data = {
            'data': {
                'type': 'players',
                'attributes': {
                    'name': 'Alice',
                    'email': 'awesome@mail.com',
                    'password': 'password'
                }
            }
        }
        response = self.client.post('/players/', data, format='json')

        content = response.content.decode()
        root = json.loads(content)
        data = root['data']
        self.assertIn('links', data.keys())
        self.assertIn('self', data['links'].keys())
        self_id = root['data']['id']
        self_link = data['links']['self']
        correct_link = '/players/%d/' % (self_id,)
        self.assertEqual(self_link, correct_link)

        response = self.client.get('/players/', format='json')
        content = response.content.decode()
        root = json.loads(content)
        self_link = root['data'][0]['links']['self']
        self.assertEqual(self_link, correct_link)


class PlayerDetailViewTest(APITestCase):
    def test_players_id_url_resolves_to_player_detail_view(self):
        found = resolve('/players/5/')
        self.assertEqual(found.func, player_detail)

    def test_displays_correct_player(self):
        correct_player = User.objects.create_user(username='DetailUser')
        User.objects.create_user(username='SecondUser')

        response = self.client.get('/players/%d/' % (correct_player.id,))

        self.assertContains(response, 'DetailUser')
        self.assertNotContains(response, 'SecondUser')

    def test_related_to_homeplanet(self):
        user = User.objects.create_user(username='SecondUser')

        response = self.client.get('/players/%d/' % (user.id,))
        content = response.content.decode()
        root = json.loads(content)
        self.assertIn('relationships', root['data'].keys())
        self.assertIsInstance(root['data']['relationships'], dict)
        self.assertIn('homeplanet', root['data']['relationships'].keys())
        homeplanet = root['data']['relationships']['homeplanet']


class UserModelTest(TestCase):
    def test_creating_and_retrieving_users(self):
        User.objects.create_user(username='First (ever) User')
        User.objects.create_user(username='User the second')

        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 2)

        first_saved_user = saved_users[0]
        second_saved_user = saved_users[1]
        self.assertEqual(first_saved_user.username, 'First (ever) User')
        self.assertEqual(second_saved_user.username, 'User the second')


