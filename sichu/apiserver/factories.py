import factory
from oauth2app.models import Client, AccessToken

from cabinet.factories import UserFactory


class ClientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Client

    user = factory.SubFactory(UserFactory)


class AccessTokenFactory(factory.DjangoModelFactory):
    class Meta:
        model = AccessToken
