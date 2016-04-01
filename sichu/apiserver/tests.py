import json

from django.test import TestCase

from cabinet.factories import UserFactory
from factories import ClientFactory, AccessTokenFactory


class BookOwnTest(TestCase):
    fixtures = ['users.json', 'client.json', 'books.json',
                'bookownerships.json']

    def setUp(self):
        self.bob = UserFactory(username='bob')
        client = ClientFactory()
        self.token = AccessTokenFactory(client=client, user=self.bob)

    def test_get(self):
        response = self.client.get(
            '/v1/bookown/?format=json',
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'meta'))

        response = self.client.get(
            '/v1/bookown/?format=json&id__exact=1',
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'meta'))

        # get friends books
        response = self.client.get(
            '/v1/bookown/?format=json&uid=2&trim_owner=1',
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'meta'))
