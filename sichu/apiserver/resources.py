from django.contrib.auth.models import User
from django.core.serializers import json
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from oauth2app.authenticate import JSONAuthenticator, \
    AuthenticationException
from tastypie import fields
from tastypie import http
from tastypie.api import Api
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from apiserver.models import OperationLog
from cabinet.models import *
from gravatar.templatetags.gravatar import gravatar_for_user


ERROR_CODES = {
    # general errors
    u'6000': (u'OK', u'OK'),
    u'6001': (u'You should call this API with POST method!', u'You should call this API with POST method!'),
    u'6002': (u'Form error', u'Form parameter error!'),
    u'6003': (u'Server Exception', u'Server exception, please debug it!'),

    # bookown api errors
    u'6100': (u'Book with the ISBN not found!', 
              u'Book with the ISBN not found!'),
    u'6101': (u'Bookown not found!', u'Bookown not found!'),
    u'6102': (u'Bookown not yours!', u'Bookown not yours!'),
    u'6103': (u'Status is not valid!', u'Status is not valid!'),
    u'6104': (u'Email not valid!', u'Email not valid!'),

    # bookborrowreq api errors
    u'6201': (u'No such bookborrowreq!',
              u'No such bookborrowreq!'),
    u'6202': (u'Bookborrowreq authorization failed!',
              u'Bookborrowreq authorization failed!'),

    # friends api errors
    u'6301': (u'No such weibo user!', u'No such weibo user!'),
    u'6302': (u'This weibo user has unbind!', u'This weibo user has unbind'),

    # bookborrowrec api errors
    u'6401': (u'No such bookborrowrec!',
              u'No such bookborrowrec!'),
    u'6402': (u'Bookborrowrec authorization failed!',
              u'Bookborrowrec authorization failed!'),

    # account api errors
    u'6501': (u'No such user!', u'No such user!'),
    u'6502': (u'username error!', u'username error!'),
    u'6503': (u'email error!', u'email error!'),

    # task api errors
    u'6601': (u'No such export log.', u'No such export log.'),
}


def set_errors(ret, err_code, err_msg=None):
    ret[u'error_code'] = err_code
    if err_msg is None:
        ret[u'error_message'] = ERROR_CODES[err_code][0]
    else:
        ret[u'error_message'] = err_msg


class OAuthAuthentication(Authentication):
    def __init__(self, scopes=None):
        self.scopes = scopes
        self.authenticator = JSONAuthenticator(scope=self.scopes)

    def is_authenticated(self, request, **kwargs):
        try:
            self.authenticator.validate(request)
            request.user = self.authenticator.user
            return True
        except AuthenticationException:
            return False

    def get_identifier(self, request):
        return request.user.username


class PrettyJSONSerializer(Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)


class UserResource(ModelResource):
    books   = fields.IntegerField()
    borrows = fields.IntegerField()
    loans   = fields.IntegerField()
    avatar  = fields.CharField()
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()
        fields = ('id', 'username', 'first_name', 'last_name')

    def dehydrate_username(self, bundle):
        return bundle.obj.get_nickname()

    def dehydrate_books(self, bundle):
        return bundle.obj.book_num()

    def dehydrate_borrows(self, bundle):
        return bundle.obj.bookborrowrecord_set.count()

    def dehydrate_loans(self, bundle):
        return len(bundle.obj.book_loaned())

    def dehydrate_avatar(self, bundle):
        return bundle.obj.get_avatar()


class BookResource(ModelResource):
    cover = fields.CharField()
    class Meta:
        queryset = Book.objects.all()
        resource_name = 'book'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()

    def dehydrate_cover(self, bundle):
        return bundle.obj.get_image_url()


class BookOwnershipResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner')
    book  = fields.ForeignKey(BookResource, 'book')
    class Meta:
        queryset = BookOwnership.objects.all()
        resource_name = 'bookown'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()
        filtering = {'id': ('exact',)}
        
    def authorized_read_list(self, object_list, bundle):
        uid = bundle.request.GET.get('uid')
        self.trim_owner = bundle.request.GET.get('trim_owner')
        if uid is None:
            return object_list.filter(owner=bundle.request.user).order_by('-id')
        else:
            query = Q(owner__id=uid)
            query &= ~Q(status="5")
            try:
                Follow.objects.get(following=bundle.request.user, user__id=uid)
                query &= Q(visible__lte=2)
            except Follow.DoesNotExist:
                query &= Q(visible=1)
            return object_list.filter(query).order_by('-id')

    def dehydrate_book(self, bundle):
        book_bundle = res_book.build_bundle(obj=bundle.obj.book)
        res_book.full_dehydrate(book_bundle)
        return book_bundle

    def dehydrate_owner(self, bundle):
        if hasattr(self, 'trim_owner') and self.trim_owner == '1':
            return bundle.obj.owner.id
        user_bundle = res_user.build_bundle(obj=bundle.obj.owner)
        res_user.full_dehydrate(user_bundle)
        return user_bundle


class BookBorrowRecResource(ModelResource):
    ownership = fields.ForeignKey(BookOwnershipResource, 'ownership')
    borrower  = fields.ForeignKey(UserResource, 'borrower')
    class Meta:
        queryset = BookBorrowRecord.objects.all()
        resource_name = 'bookborrow'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()
        
    def authorized_read_list(self, object_list, bundle):
        as_borrower = bundle.request.GET.get('as_borrower')
        if as_borrower is not None:
            if as_borrower == "1":
                return object_list.filter(borrower=bundle.request.user).\
                    order_by('returned_date')
            else:
                return object_list.filter(ownership__owner=bundle.request.user).\
                    order_by('returned_date')
        return object_list.filter(
            Q(ownership__owner=bundle.request.user) | 
            Q(borrower=bundle.request.user)).order_by('returned_date')

    def dehydrate_ownership(self, bundle):
        bookown_bundle = res_bookown.build_bundle(obj=bundle.obj.ownership)
        res_bookown.full_dehydrate(bookown_bundle)
        return bookown_bundle

    def dehydrate_borrower(self, bundle):
        user_bundle = res_user.build_bundle(obj=bundle.obj.borrower)
        res_user.full_dehydrate(user_bundle)
        return user_bundle

    def dehydrate_borrow_date(self, bundle):
        return str(bundle.obj.borrow_date)

    def dehydrate_planed_return_date(self, bundle):
        return str(bundle.obj.planed_return_date)

    def dehydrate_returned_date(self, bundle):
        if bundle.obj.returned_date is not None:
            return str(bundle.obj.returned_date)
        return None

class BookBorrowRec2Authorization(Authorization):

    def create_detail(self, object_list, bundle):
        if not bundle.data.has_key('ownership'):
            return False

        try:
            BookOwnership.objects.get(
                id=bundle.data['ownership'],
                owner=bundle.request.user)
            return True
        except BookOwnership.DoesNotExist:
            return False

    def update_detail(self, object_list, bundle):
        return bundle.obj.ownership.owner == bundle.request.user

    def delete_detail(self, object_list, bundle):
        return bundle.obj.ownership.owner == bundle.request.user


class BookBorrowRec2Resource(ModelResource):
    ownership = fields.ForeignKey(BookOwnershipResource, 'ownership')
    class Meta:
        queryset = BookBorrowRecord2.objects.all()
        resource_name = 'bookborrow2'
        authorization= BookBorrowRec2Authorization()
        authentication = OAuthAuthentication()

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(
            Q(ownership__owner=bundle.request.user)).order_by('returned_date')

    def dehydrate_ownership(self, bundle):
        bookown_bundle = res_bookown.build_bundle(obj=bundle.obj.ownership)
        res_bookown.full_dehydrate(bookown_bundle)
        return bookown_bundle

    def dehydrate_borrow_date(self, bundle):
        return str(bundle.obj.borrow_date)

    def dehydrate_returned_date(self, bundle):
        if bundle.obj.returned_date is not None:
            return str(bundle.obj.returned_date)
        return None

    def hydrate_ownership(self, bundle):
        obj = BookOwnership.objects.get(id=bundle.data['ownership'])
        bundle.data['ownership'] = obj
        return bundle


class OperationLogResource(ModelResource):
    class Meta:
        queryset = OperationLog.objects.all()
        resource_name = 'oplog'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()
        excludes = ['users']
        filtering = {'id': ('gt'),
                     'model': ('exact')}

    def authorized_read_list(self, object_list, bundle):
        if bundle.request.GET.get('latest') is not None:
            return [object_list.filter(
                    users=bundle.request.user).latest(field_name='id')]
        return object_list.filter(users=bundle.request.user).order_by('id')


class FollowResource(ModelResource):
    following = fields.ForeignKey(UserResource, 'following')
    user      = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = Follow.objects.all()
        resource_name = 'follow'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()        

    def authorized_read_list(self, object_list, bundle):
        as_follower = bundle.request.GET.get('as_follower')
        if as_follower is not None:
            if as_follower == "1":
                return object_list.filter(following=bundle.request.user)
            else:
                return object_list.filter(user=bundle.request.user)
        return object_list.filter(
            Q(user=bundle.request.user) | Q(following=bundle.request.user))

    def dehydrate_following(self, bundle):
        user_bundle = res_user.build_bundle(obj=bundle.obj.following)
        res_user.full_dehydrate(user_bundle)
        return user_bundle

    def dehydrate_user(self, bundle):
        user_bundle = res_user.build_bundle(obj=bundle.obj.user)
        res_user.full_dehydrate(user_bundle)
        return user_bundle


class BookBorrowReqAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if object is None:
            return True

        if object.bo_ship.owner == request.user:
            return True

        return False


class BookBorrowReqResource(ModelResource):
    requester = fields.ForeignKey(UserResource, 'requester')
    bo_ship   = fields.ForeignKey(BookOwnershipResource, 'bo_ship')
    class Meta:
        queryset = BookBorrowRequest.objects.all()
        resource_name = 'bookborrowreq'
        serializer = PrettyJSONSerializer()
        authentication = OAuthAuthentication()
        authorization = BookBorrowReqAuthorization()
        allowed_methods = ['get', 'put']
        always_return_data = True

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(bo_ship__owner=bundle.request.user).\
            order_by('-datetime')

    def dehydrate_bo_ship(self, bundle):
        bo_ship_bundle = res_bookown.build_bundle(obj=bundle.obj.bo_ship)
        res_bookown.full_dehydrate(bo_ship_bundle)
        return bo_ship_bundle

    def dehydrate_requester(self, bundle):
        user_bundle = res_user.build_bundle(obj=bundle.obj.requester)
        res_user.full_dehydrate(user_bundle)
        return user_bundle

    def dehydrate_datetime(self, bundle):
        return str(bundle.obj.datetime)

    def dehydrate_planed_return_date(self, bundle):
        return str(bundle.obj.planed_return_date)


res_user       = UserResource()
res_book       = BookResource()
res_bookown    = BookOwnershipResource()
res_oplog      = OperationLogResource()
res_bookbrw    = BookBorrowRecResource()
res_bookbrw2   = BookBorrowRec2Resource()
res_follow     = FollowResource()
res_bookbrwreq = BookBorrowReqResource()

v1_api = Api(api_name='v1')
v1_api.register(res_user)
v1_api.register(res_book)
v1_api.register(res_bookown)
v1_api.register(res_oplog)
v1_api.register(res_bookbrw)
v1_api.register(res_bookbrw2)
v1_api.register(res_follow)
v1_api.register(res_bookbrwreq)
