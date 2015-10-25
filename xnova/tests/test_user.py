import json
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
    def test_user_list_returns_valid_json_api(self):
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
                'name': 'PostUser',
                'email': 'post@example.com',
                'password': 'password'
            }
        }, format='json')
        response = user_list(request)
        self.assertIn('PostUser', response.content.decode())
        expected_json = {
            'data': {
                'type': 'users',
                'name': 'PostUser',
                'email': 'post@example.com'
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
