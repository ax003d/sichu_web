from django.conf.urls import patterns, include, url

from apiserver.resources import v1_api

urlpatterns = patterns(
    'apiserver.views',
    (r'^v1/account/register/$', 'account__register'),
    (r'^v1/account/login/$', 'account__login'),
    (r'^v1/account/login_by_weibo/$', 'account__login_by_weibo'),
    (r'^v1/account/unbind_weibo/$', 'account__unbind_weibo'),
    (r'^v1/account/bind_weibo/$', 'account__bind_weibo'),
    (r'^v1/account/may_know/$', 'account__may_know'),
    (r'^v1/account/update_gexinid/$', 'account__update_gexinid'),
    (r'^v1/account/numbers/$', 'account__numbers'),
    (r'^v1/account/email_verify/$', 'account__email_verify'),
    #   v1/book/ # Get BookResource
    #   v1/bookown/ # Get BookOwnershipResource
    (r'^v1/bookown/add/$', 'bookown__add'),
    (r'^v1/bookown/delete/(?P<bo_id>.*)/$', 'bookown__delete'),
    (r'^v1/bookown/export/$', 'bookown__export'),
    (r'^v1/bookown/(?P<bo_id>.*)/$', 'bookown__edit'),
    #   v1/bookborrow/ # Get BookBorrowRecResource
    (r'^v1/bookborrow/(?P<rec_id>.*)/$', 'bookborrow__detail'),
    #  ^v1/bookborrowreq/ # Get BookBorrowReqResource
    (r'^v1/bookborrowreq/(?P<req_id>.*)/$', 'bookborrowreq__detail'),
    (r'^v1/friends/follow/$', 'friends__follow'),
    #   v1/follow/ # Get FollowResource
    #   v1/oplog/ # Get OperationLogResource
    (r'^v1/request/bookborrow/$', 'bookborrow__add'),
    #  ^v1/user/ # Get UserResource

    (r'^v1/task/export/$', 'task__export'),

    (r'^v1/monitor/push_notification/$', 'monitor__push_notification'),
    (r'^v1/monitor/error_report/$', 'monitor__error_report'),
    (r'^v1/monitor/test_email/$', 'monitor__test_email'),
    (r'^v1/monitor/logging_and_http/$', 'monitor__logging_and_http'),
    (r'^', include(v1_api.urls)),
)
