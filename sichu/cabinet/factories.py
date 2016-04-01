import factory

from django.contrib.auth.models import User
from cabinet.models import Book


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User


class BookFactory(factory.DjangoModelFactory):
    class Meta:
        model = Book
    isbn = factory.Faker('ean13')
    title = factory.Faker('sentence')
    author = factory.Faker('first_name')
