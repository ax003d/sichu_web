import json

from django.test import TestCase

from cabinet.factories import UserFactory, BookOwnFactory
from factories import ClientFactory, AccessTokenFactory


class BookOwnTest(TestCase):
    fixtures = ['users.json', 'client.json', 'books.json',
                'bookownerships.json']

    def setUp(self):
        self.bob = UserFactory(username='bob')
        client = ClientFactory()
        self.token = AccessTokenFactory(client=client, user=self.bob)
        self.book = BookOwnFactory(owner=self.bob)

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

    def test_add(self):
        response = self.client.post(
            '/v1/bookown/add/?format=json',
            {'isbn': self.book.book.isbn,
             'status': '1'},
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'id'))

    def test_edit(self):
        response = self.client.post(
            '/v1/bookown/{}/'.format(self.book.id),
            {'status': '5',
             'remark': 'test'},
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'error_code'))

        response = self.client.post(
            '/v1/bookown/{}/'.format(self.book.id),
            {'status': '4',
             'remark': 'test'},
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'status'))

    def test_delete(self):
        response = self.client.post(
            '/v1/bookown/delete/{}/'.format(self.book.id),
            HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        # print response.content
        ret = json.loads(response.content)
        self.assertTrue(ret.has_key(u'status'))
