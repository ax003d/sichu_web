from oauth2app.authenticate import JSONAuthenticator, AuthenticationException
from oauth2app.models import AccessRange

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.


class scope_required(object):
    """
    OAuth 2.0 scope required decorator.
    """

    def __init__(self, *scopes):
        self.scopes = None
        try:
            self.scopes = [ AccessRange.objects.get(key=s) for s in scopes ]
        except AccessRange.DoesNotExist:
            pass


    def __call__(self, view_func):
        def wrapped_view(*args, **kwargs):
            request = args[0]
            authenticator = JSONAuthenticator(scope=self.scopes)
            try:
                authenticator.validate(request)
                request.user = authenticator.user
            except AuthenticationException:
                return authenticator.error_response()
            return view_func(*args, **kwargs)
        return wraps(view_func)(wrapped_view)

