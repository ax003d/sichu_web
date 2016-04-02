from django.test.client import Client
from django.test import TestCase
from models import User
from factories import BookFactory


class BookTest(TestCase):

    def setUp(self):
        self.book = BookFactory()

    def test_search_isbn(self):
        response = self.client.get(
            '/cabinet/search/', {'keyword': self.book.isbn})
        ctx = response.context
        self.assertEqual(len(ctx['books']), 1)

    def test_search_title(self):
        response = self.client.get(
            '/cabinet/search/', {'keyword': self.book.title})
        ctx = response.context
        self.assertEqual(len(ctx['books']), 1)

    def test_search_author(self):
        response = self.client.get(
            '/cabinet/search/', {'keyword': self.book.author})
        ctx = response.context
        self.assertEqual(len(ctx['books']), 1)