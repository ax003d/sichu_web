# coding: utf-8

import ucsv as csv
import logging
import sys
import StringIO

from datetime import datetime
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email, ValidationError
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Template, Context
from django.utils import simplejson, timezone
from django.views.decorators.csrf import csrf_exempt

from oauth2app.models import Client, AccessToken

from pygetui.getui import GXPushClient, PUSH_TYPE_NOTIFY, PUSH_TYPE_LINK

from apiserver.decorators import scope_required
from apiserver.forms import LoginForm, BookBorrowRequestForm, \
    RegisterForm
from apiserver.models import *
from apiserver.resources import set_errors, res_bookown, \
    res_bookbrwreq, res_bookbrw
from cabinet.forms import BookOwnForm
from cabinet.models import WeiboUser, BookBorrowRequest, BookOwnership, \
    Follow, BookBorrowRecord
from cabinet.utils import add_book
from gravatar.templatetags.gravatar import gravatar_for_user

EXP_TITLE = u'您的书籍列表已导出'
EXP_SUBJECT = u"""
亲爱的 {{ user }},

您的书籍列表已导出, 请查看附件!
（注意：本附件可以使用WPS表格软件直接打开；如果您使用的是Excel，请先用记事本将附件以ASCII编码格式另存，然后就可以使用Excel打开）
感谢您的使用！

-------
这封邮件来自私橱网 sichu.sinaapp.com
"""

logger = logging.getLogger('django.request')
getui = GXPushClient(appid=settings.GX_APPID,
                     appkey=settings.GX_APPKEY,
                     mastersecret=settings.GX_MASTERSECRET)

def _render_json_repsonse(ret):
    json = simplejson.dumps(ret)
    return HttpResponse(json, mimetype='application/json')    


def _set_token(user, client, ret):
    for t in AccessToken.objects.filter(client=client, user=user):
        t.delete()
    token = AccessToken(client=client, user=user)
    token.save()
    ret['token'] = token.token
    ret['refresh_token'] = token.refresh_token
    ret['expire'] = token.expire
    ret['refreshable'] = token.refreshable
    ret['uid'] = user.id
    ret['username'] = user.username
    ret['avatar'] = gravatar_for_user(user)
    ret['email'] = user.get_verified_email()


@csrf_exempt
def account__register(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        form = RegisterForm(request.POST)
        if not form.is_valid():
            if form.errors.has_key('username'):
                set_errors(ret, u'6502', form.errors['username'])
            elif form.errors.has_key('email'):
                set_errors(ret, u'6503', form.errors['email'])
            else:
                set_errors(ret, u'6002', form.errors)
            return _render_json_repsonse(ret)

        user = form.save()
        user.set_password(form.cleaned_data['password'])
        user.save()
        client = Client.objects.get(key=request.POST.get('apikey'))
        _set_token(user, client, ret)
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@csrf_exempt
def account__login(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        form = LoginForm(request.POST)
        if not form.is_valid():
            set_errors(ret, u'6002', form.errors)
            return _render_json_repsonse(ret)
        
        cd = form.cleaned_data
        user = User.objects.get(username=cd['username'])
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        client = Client.objects.get(key=cd['apikey'])
        for t in AccessToken.objects.filter(client=client, user=user):
            t.delete()
        token = AccessToken(client=client, user=user)
        token.save()
        ret['token'] = token.token
        ret['refresh_token'] = token.refresh_token
        ret['expire'] = token.expire
        ret['refreshable'] = token.refreshable
        ret['uid'] = user.id
        ret['username'] = user.username
        ret['avatar'] = gravatar_for_user(user)
        ret['email'] = user.get_verified_email()
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@csrf_exempt
def account__login_by_weibo(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        uid = request.POST.get('uid')
        screen_name = request.POST.get('screen_name')
        profile_image_url = request.POST.get('profile_image_url')
        access_token = request.POST.get('access_token')
        expires_in = int(request.POST.get('expires_in'))
        apikey = request.POST.get('apikey')

        wu, create = WeiboUser.objects.get_or_create(
            uid=uid,
            defaults={'token': access_token,
                      'expires_in': expires_in})
        wu.update(screen_name, 
                  profile_image_url, 
                  access_token, 
                  expires_in)
        wu.save()

        if wu.user is None:
            user, create = User.objects.get_or_create(username=uid)
            if create:
                user.first_name = screen_name
                user.set_unusable_password()
                user.save()
            wu.user = user
            wu.save()

        user = wu.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        client = Client.objects.get(key=apikey)
        for t in AccessToken.objects.filter(client=client, user=user):
            t.delete()
        token = AccessToken(client=client, user=user)
        token.save()
        ret['token'] = token.token
        ret['refresh_token'] = token.refresh_token
        ret['expire'] = token.expire
        ret['refreshable'] = token.refreshable
        ret['uid'] = user.id
        ret['username'] = user.username
        ret['avatar'] = gravatar_for_user(user)
        ret['email'] = user.get_verified_email()
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def account__unbind_weibo(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        wu = request.user.get_weibo()
        if wu is not None:
            wu.user = None
            wu.save()
        ret['status'] = 'OK'
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def account__bind_weibo(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        uid = request.POST.get('uid')
        screen_name = request.POST.get('screen_name')
        profile_image_url = request.POST.get('profile_image_url')
        access_token = request.POST.get('access_token')
        expires_in = int(request.POST.get('expires_in'))

        wu, create = WeiboUser.objects.get_or_create(
            uid=uid,
            defaults={'token': access_token,
                      'expires_in': expires_in})
        wu.update(screen_name, 
                  profile_image_url, 
                  access_token, 
                  expires_in)
        wu.user = request.user
        wu.save()
        ret['status'] = 'OK'
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def account__may_know(request):
    ret = {}
    # this method will not make change to the DB
    # but weibo ids will be large, so we use POSt here
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        wb_ids = request.POST.get('wb_ids')
        ret['may_know'] = []
        follows = [ i.following for i in request.user.follow_set.all() ]
        ret['friends']  = [ i.get_weibo().uid for i in follows if i.get_weibo() is not None ]
        if wb_ids is None:
            return _render_json_repsonse(ret)

        wb_ids = wb_ids.split(',')        
        ret['may_know'] = [ i.uid for i in WeiboUser.objects.filter(uid__in=wb_ids).exclude(user=None).exclude(user__in=follows) ]
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def account__update_gexinid(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)
    
    try:
        client_id = request.POST.get('client_id')
        if client_id is None:
            ret['status'] = False
            return _render_json_repsonse(ret)

        GexinID.objects.filter(
            Q(client_id=client_id) & ~Q(user=request.user)).delete()
        if request.user.gexinid_set.count() == 0:
            gexin = GexinID(client_id=client_id, user=request.user)
            gexin.save()
        else:
            gexin = request.user.gexinid_set.all()[0]
            gexin.client_id = client_id
            gexin.save()
        ret['status'] = True
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def account__numbers(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        uid = request.POST.get('uid')
        user = User.objects.get(id=uid)
        ret['total'] = user.book_num()
        ret['loaned'] = len(user.book_loaned())
        ret['borrowed'] = user.bookborrowrecord_set.count()
    except User.DoesNotExist:
        set_errors(ret, u'6501')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def account__email_verify(request):
    ret = {}
    try:
        email = request.GET.get('email')
        validate_email(email)
        ev = EmailVerify(
            email=email, 
            code=uuid1().hex,
            user=request.user)
        ev.save()
        ret['OK'] = 'OK'
    except ValidationError:
        set_errors(ret, u'6503')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookown__add(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        book = add_book(request.POST['isbn'])
        if book == None:
            set_errors(ret, u'6100')
            return _render_json_repsonse(ret)

        request.POST = request.POST.copy()
        request.POST['owner'] = request.user.id
        request.POST['book'] = book.id
        form = BookOwnForm(request.POST)
        if not form.is_valid():
            set_errors(ret, u'6002', form.errors)
            return _render_json_repsonse(ret)
        
        own = form.save()
        bundle = res_bookown.build_bundle(obj=own)
        return HttpResponse(
            res_bookown.serialize(None, res_bookown.full_dehydrate(bundle), 
                                  'application/json'),
            mimetype='application/json')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookown__edit(request, bo_id):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        bo = get_object_or_404(BookOwnership, id=bo_id)
        if bo.owner != request.user:
            set_errors(ret, u'6102')
            return _render_json_repsonse(ret)

        status = request.POST.get('status')
        remark = request.POST.get('remark')

        if (status is not None) and (status in ['1', '2', '3', '4']):
            bo.status = status
        else:
            set_errors(ret, u'6103')
            return _render_json_repsonse(ret)
        if remark is not None:
            bo.remark = remark
        bo.save()
        ret['status'] = u'OK'
    except Http404:
        set_errors(ret, u'6101')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookown__export(request):
    ret = {}
    email = request.POST.get('email')
    try:
        el = ExportLog(email=email, user=request.user)
        el.clean_fields()
        el.save()
        ret['OK'] = 'OK'
    except ValidationError:
        set_errors(ret, u'6104')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookown__delete(request, bo_id):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        bo = get_object_or_404(BookOwnership, id=bo_id)
        if bo.owner != request.user:
            set_errors(ret, u'6102')
            return _render_json_repsonse(ret)

        bo.delete()
        ret['status'] = u'OK'
    except Http404:
        set_errors(ret, u'6101')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookborrow__add(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    try:
        bo_ship = request.POST.get('bo_ship')
        if len(BookBorrowRequest.objects.filter(
                bo_ship=bo_ship, 
                requester=request.user, 
                status=0)) != 0:
            ret['status'] = u'OK'
            return _render_json_repsonse(ret)

        request.POST = request.POST.copy()
        request.POST['requester'] = request.user.id
        form = BookBorrowRequestForm(request.POST)
        if not form.is_valid():
            set_errors(ret, u'6002', form.errors)
            return render_json_repsonse(ret)
        
        bbr = form.save()
        ret['status'] = u'OK'
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookborrow__detail(request, rec_id):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    rec = None
    try:
        rec = get_object_or_404(BookBorrowRecord, id=rec_id)
    except Http404:
        set_errors(ret, u'6401')
        return _render_json_repsonse(ret)

    if rec.ownership.owner != request.user:
        set_errors(ret, u'6402')
        return _render_json_repsonse(ret)

    try:        
        rec.returned_date = datetime.now()
        rec.save()
        rec.ownership.status = u'1'
        rec.ownership.save()
        bundle = res_bookbrw.build_bundle(obj=rec)
        return HttpResponse(
            res_bookbrw.serialize(None, 
                                  res_bookbrw.full_dehydrate(bundle), 
                                  'application/json'),
            mimetype='application/json')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def bookborrowreq__detail(request, req_id):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    req = None
    try:
        req = get_object_or_404(BookBorrowRequest, id=req_id)
    except Http404:
        set_errors(ret, u'6201')
        return _render_json_repsonse(ret)

    if req.bo_ship.owner != request.user:
        set_errors(ret, u'6202')
        return _render_json_repsonse(ret)

    try:        
        status = request.POST.get('status')
        if status is not None:
            req.status = status
            req.save()
        bundle = res_bookbrwreq.build_bundle(obj=req)
        return HttpResponse(
            res_bookbrwreq.serialize(None, 
                                     res_bookbrwreq.full_dehydrate(bundle), 
                                     'application/json'),
            mimetype='application/json')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@scope_required()
@csrf_exempt
def friends__follow(request):
    ret = {}
    if request.method != 'POST':
        set_errors(ret, u'6001')
        return _render_json_repsonse(ret)

    wb_id = request.POST.get('wb_id')
    remark = request.POST.get('remark')
    remark = remark if remark is not None else ''
    try:
        wu = get_object_or_404(WeiboUser, uid=wb_id)
        if wu.user is None:
            set_errors(ret, u'6302')
            return _render_json_repsonse(ret)
        follow = Follow.objects.get(following=wu.user, user=request.user)
        ret['status'] = u'OK'
        ret['uid'] = wb_id
    except Http404:
        set_errors(ret, u'6301')
        return _render_json_repsonse(ret)
    except Follow.DoesNotExist:
        follow = Follow(following=wu.user, remark=remark, user=request.user)
        follow.save()
        ret['status'] = u'OK'
        ret['uid'] = wb_id
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')

    return _render_json_repsonse(ret)


@csrf_exempt
def task__export(request):
    """
    For task queue. Not for direct access.
    """
    ret = {}
    eid = request.POST.get('eid')
    try:
        el = get_object_or_404(ExportLog, id=eid)
        if el.status == ExportStatus.succeed:
            ret['OK'] = 'OK'
            return _render_json_repsonse(ret)

        exp = StringIO.StringIO()
        cw = csv.writer(exp)
        cw.writerow([u'书名', u'状态', u'备注', u'链接'])
        for i in el.user.bookownership_set.all():
            cw.writerow([
                    i.book.title, 
                    i.get_status_display(), 
                    i.remark, 
                    'http://sichu.sinaapp.com/cabinet/book/%d/' % i.book.id])
        # send email            
        t = Template(EXP_SUBJECT)
        c = Context({'user': el.user.get_nickname()})
        body = t.render(c)
        message = EmailMultiAlternatives(
            subject=EXP_TITLE.encode('utf-8'), 
            body=body.encode('utf-8'),
            from_email=settings.EMAIL_HOST_USER, 
            to=[el.email])
        message.attach('books.csv', exp.getvalue(), 'text/csv; charset=UTF-8')
        message.send(fail_silently=False)
        exp.close()
        el.status = ExportStatus.succeed.value
        el.save()
        ret['OK'] = 'OK'
    except Http404:
        set_errors(ret, u'6601')
    except Exception:
        logger.exception(str(sys._getframe().f_code.co_name))
        set_errors(ret, u'6003')
        el.status = ExportStatus.failed.value
        el.save()

    return _render_json_repsonse(ret)
    

def monitor__push_notification(request):
    push_type = request.GET.get('push_type')
    test_client = 'f7da8a44ba2b0780d545df95e54af26a'
    if push_type == '1':
        getui.push_notification('link title', 'link message', 
                                PUSH_TYPE_LINK, [test_client],
                                link='http://sichu.sinaapp.com')
    elif push_type == '2':
        getui.push_notification('notify title', 'notify message', 
                                PUSH_TYPE_NOTIFY, [test_client])
    return HttpResponse('notification sent')


def monitor__error_report(request):
    raise Exception('Manually raised error, you should recieve email!')


def monitor__test_email(request):
    message = EmailMultiAlternatives(
        subject='test email', 
        body="Can you receive email?",
        from_email=settings.EMAIL_HOST_USER, 
        to=[request.GET.get('email')])
    message.send(fail_silently=False)
    return HttpResponse('email sent')


def monitor__logging_and_http(request):
    try:
        raise Exception("logging exception")
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))

    return HttpResponse('Check email for exception logging!')
