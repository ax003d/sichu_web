import models


class WeiboBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = True

    def authenticate(self, wid=None):
        try:
            wu = models.WeiboUser.objects.get(uid=wid)
            return wu.user
        except models.WeiboUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return models.User.objects.get(pk=user_id)
        except models.User.DoesNotExist:
            return None
