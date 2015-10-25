import json
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from xnova.views import user_list


class UserListTest(TestCase):
    def setUp(self):
        self.rf = APIRequestFactory()

    def test_users_url_resolves_to_user_list_view(self):
        found = resolve('/users/')
        self.assertEqual(found.func, user_list)

    # TODO
    # jsonapi.org
    def test_user_list_returns_valid_jsonapi(self):
        request = self.rf.get('/users/', format='json')
        response = user_list(request)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

        content = response.content.decode()
        root = json.loads(content)
        self.assertIsInstance(root, dict)
        self.assertTrue('data' in root or 'errors' in root or 'meta' in root)
        valid_members = ('data', 'errors', 'meta', 'jsonapi', 'links', 'included')
        for member in root:
            self.assertIn(member, valid_members)

        if 'data' not in root:
            self.assertNotIn('included', root,
                             "If a document does not contain a top-level data "
                             "key, the included member MUST NOT be present "
                             "either.")

    def test_user_list_can_save_a_POST_request(self):
        request = self.rf.post('/users/', {
            'data': {
                'type': 'users',
                'attributes': {
                    'name': 'PostUser',
                    'email': 'post@example.com',
                    'password': 'password'
                }
            }
        }, format='json')

        response = user_list(request)

        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.first()
        self.assertEqual(new_user.username, 'PostUser')

        self.assertIn('PostUser', response.content.decode())
        expected_json = {
            'data': {
                'type': 'users',
                'attributes': {
                    'name': 'PostUser',
                    'email': 'post@example.com'
                }
            }
        }
        self.assertJSONEqual(response.content.decode(), expected_json)

    def test_user_list_returns_data_array(self):
        request = self.rf.get('/users/', format='json')
        response = user_list(request)

        content = response.content.decode()
        root = json.loads(content)
        self.assertIn('data', root.keys())
        self.assertIsInstance(root['data'], list)

    def test_user_list_displays_all_users_attributes(self):
        User.objects.create_user('Alice', email='alice@example.com')
        User.objects.create_user('Bob', email='bob@example.com')

        request = self.rf.get('/users/', format='json')
        response = user_list(request)
        content = json.loads(response.content.decode())

        self.assertEqual({
            'name': 'Alice',
            'email': 'alice@example.com'
        }, content['data'][0]['attributes'])
        self.assertEqual({
            'name': 'Bob',
            'email': 'bob@example.com'
        }, content['data'][1]['attributes'])


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
