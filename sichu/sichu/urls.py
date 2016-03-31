import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apiserver.resources import v1_api

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cabinet/', include('cabinet.urls')),
)

if 'SERVER_SOFTWARE' not in os.environ:
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('cabinet.views',
    url(r'^$', 'login'),
    url(r'^accounts/login/$',  'login'),    
    url(r'^accounts/logout/$',  'sc_logout'),
    url(r'^registration/password_reset/$', 'password_reset'),
    url(r'^callback/weibo/authorize/$', 'callback_weibo_auth'),
    url(r'^monitor/mc/$', 'monitor__mc'),
)


urlpatterns += patterns('django.contrib.auth.views',
    url(r'^registration/password_reset_done/$', 'password_reset_done'),
    url(r'^registration/password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm'),
    url(r'^registration/password_reset_complete/$', 'password_reset_complete'),
)


urlpatterns += patterns('apiserver',
    (r'^', include('apiserver.urls')),
)
