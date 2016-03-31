# coding: utf-8

import logging
import os
import socket
import time

from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template import Template, Context
from django.utils import simplejson

from pygetui.getui import GXPushClient, PUSH_TYPE_NOTIFY
from apiserver.models import OP_ADD, OP_UPDATE, OP_DELETE, OperationLog, \
    ExportLog, EmailVerify
from apiserver.resources import res_bookown, res_bookbrw, res_follow, \
    res_bookbrwreq
from cabinet.models import BookOwnership, Follow, BookBorrowRequest, \
    BookBorrowRecord, CabinetNews

logger = logging.getLogger('django.request')
getui  = GXPushClient(appid=settings.GX_APPID,
                     appkey=settings.GX_APPKEY,
                     mastersecret=settings.GX_MASTERSECRET)


EMAIL_SIGNATURE = u'\n\n--------\n这封邮件来自私橱网 www.sichu8.com'

TEMPLATE_NEWS_ADD_BOOK = u"""
添加了书籍 <a href="/cabinet/bookownership/%d/" class="bookownershipinfo">%s</a>!
"""

TEMPLATE_NEWS_BORROW_BOOK = u"""
借给 <a href="/cabinet/user/%d/" class="userinfo">%s</a> 一本书: <a href="/cabinet/bookownership/%d/" class="bookownershipinfo">%s</a>!
"""

TEMPLATE_NEWS_BOOK_RETURNED = u"""
归还了书籍 <a href="/cabinet/bookownership/%d/" class="bookownershipinfo">%s</a>给 <a href="/cabinet/user/%d/" class="userinfo">%s</a>!
"""

EMAIL_VERIFY_TITLE = u'电子邮件验证'
EMAIL_VERIFY_BODY_TEXT  = u"""
亲爱的橱友，{{ username }}:

您收到这封邮件是因为您请求在私橱网验证您的电子邮箱！如果您没有发送过这样的请求，请忽略本邮件。否则，请用浏览器打开以下链接进行验证：

sichu.sinaapp.com/cabinet/email_verify/?code={{ code }}


----------
这封邮件来自私橱网 sichu.sinaapp.com
"""
EMAIL_VERIFY_BODY_HTML  = u"""
亲爱的橱友，{{ username }}:
<br/><br/>
您收到这封邮件是因为您请求在私橱网验证您的电子邮箱！<br/>
如果您没有发送过这样的请求，请忽略本邮件。否则，请点击以下链接进行邮件验证：
<br/><br/>
<a href="http://sichu.sinaapp.com/cabinet/email_verify/?code={{ code }}" target="_blank">http://sichu.sinaapp.com/cabinet/email_verify/?code={{ code }}</a>
<br/><br/>
----------<br/>
这封邮件来自私橱网 http://sichu.sinaapp.com
"""


def is_empty_text(s):
    if (s is not None) and (len(s) > 0):
        return False
    return True


def send_email(title, message, send_to):
    body = u'%s %s' % (message, EMAIL_SIGNATURE)
    message = EmailMultiAlternatives(
        subject=title.encode('utf-8'), 
        body=body.encode('utf-8'),
        from_email=settings.EMAIL_HOST_USER, 
        to=[send_to])
    try:
        message.send(fail_silently=False)
    except socket.error, e:
        logger.exception('send email error!')


def _get_adjust_timestamp():
    """
    Different instance will run on different servers, so the timestamp will
    not identical. We must sure that new OperationLog's timestamp is latter
    than the latest one!
    Maybe use id as sync key.
    """
    timestamp = time.mktime(datetime.utcnow().timetuple())
    try:
        latest_ts = OperationLog.objects.latest(field_name='id').timestamp
        if timestamp < latest_ts:
            timestamp = latest_ts + 1
    except OperationLog.DoesNotExist:
        pass
    return timestamp


def _on_instance_saved(opcode, instance, res_obj):
    bundle = res_obj.build_bundle(obj=instance)

    log = OperationLog(
        timestamp=_get_adjust_timestamp(),
        opcode=opcode,
        model=".".join([instance.__module__, instance.__class__.__name__]),
        data=res_obj.serialize(None, res_obj.full_dehydrate(bundle), 
                               'application/json'))
    log.save()
    return log


def _on_instance_deleted(instance):
    log = OperationLog(
        timestamp=_get_adjust_timestamp(),
        opcode=OP_DELETE,
        model=".".join([instance.__module__, instance.__class__.__name__]),
        data=simplejson.dumps({'id': instance.id}))
    log.save()
    return log


@receiver(post_save, sender=BookOwnership, 
          dispatch_uid='log_add_bookown_operation')
def log_add_bookown_operation(sender, instance, created, **kwargs):
    opcode = OP_ADD if created else OP_UPDATE
    log = _on_instance_saved(opcode, instance, res_bookown)
    log.users.add(instance.owner)
    log.save()
    if (not created) or (instance.visible != 1):
        return
    news = CabinetNews(
        datetime=datetime.now(),
        lead=instance.owner,
        news=TEMPLATE_NEWS_ADD_BOOK % (instance.id, instance.book.title))
    news.save()


@receiver(post_delete, sender=BookOwnership,
          dispatch_uid='log_del_bookown_operation')
def log_del_bookown_operation(sender, instance, **kwargs):
    log = _on_instance_deleted(instance)
    log.users.add(instance.owner)
    log.save()


@receiver(post_save, sender=Follow,
          dispatch_uid='on_new_follower')
def on_new_follower(sender, instance, created, **kwargs):
    opcode = OP_ADD if created else OP_UPDATE
    log = _on_instance_saved(opcode, instance, res_follow)
    log.users.add(instance.following)
    log.users.add(instance.user)
    log.save()

    if not created:
        return
    
    title = u'新粉丝'
    message = u'%s 关注了你' % instance.user.get_nickname()
    ids = instance.following.gexinid_set.all()
    client_id = ids[0].client_id if len(ids) > 0 else None
    if client_id is not None:
        getui.push_notification(
            title, message, PUSH_TYPE_NOTIFY, [client_id])
    if not is_empty_text(instance.following.email):
        send_email(title, message, instance.following.email)


@receiver(post_delete, sender=Follow,
          dispatch_uid='on_follow_deleted')
def on_follow_deleted(sender, instance, **kwargs):
    log = _on_instance_deleted(instance)
    log.users.add(instance.following)
    log.users.add(instance.user)
    log.save()


@receiver(post_save, sender=BookBorrowRequest,
          dispatch_uid='on_bookborrowrequest_saved')
def on_bookborrowrequest_saved(sender, instance, created, **kwargs):
    opcode = OP_ADD if created else OP_UPDATE
    log = _on_instance_saved(opcode, instance, res_bookbrwreq)
    log.users.add(instance.bo_ship.owner)
    log.users.add(instance.requester)
    log.save()

    if created:
        title = u'书籍借阅请求'
        message = u'%s 想借 《%s》' % (
            unicode(instance.requester.get_nickname()), 
            unicode(instance.bo_ship.book.title))
        # notify owner by gexin
        ids = instance.bo_ship.owner.gexinid_set.all()
        client_id = ids[0].client_id if len(ids) > 0 else None
        if client_id is not None:
            getui.push_notification(
                title, message, PUSH_TYPE_NOTIFY, [client_id])
        # notify owner by email
        if not is_empty_text(instance.bo_ship.owner.email):
            send_email(title, message, instance.bo_ship.owner.email)
        return
    
    # notify borrower
    owner = instance.bo_ship.owner
    borrower = instance.requester
    book = instance.bo_ship.book
    title, message = u'您借阅请求已处理', None
    if int(instance.status) == 1:
        message = u'恭喜! %s 同意将 《%s》 借给您' % (owner.username, book.title)
        rec = BookBorrowRecord(
            ownership=instance.bo_ship,
            borrower=borrower,
            borrow_date=datetime.now(),
            planed_return_date=instance.planed_return_date)
        rec.save()
        instance.bo_ship.status = u"3"
        instance.bo_ship.save()
    elif int(instance.status) == 2:
        message = u'很遗憾! %s 拒绝将 《%s》 借给您' % (owner.username, book.title)
    else:
        return
    # notify borrower by gexin
    ids = instance.requester.gexinid_set.all()
    client_id = ids[0].client_id if len(ids) > 0 else None
    if client_id is not None:
        getui.push_notification(
            title, message,
            PUSH_TYPE_NOTIFY, [client_id])
    # notify borrower by email
    if not is_empty_text(borrower.email):
        send_email(title, message, borrower.email)


@receiver(post_delete, sender=BookBorrowRequest,
          dispatch_uid='on_bookborrowrequest_deleted')
def on_bookborrowrequest_deleted(sender, instance, **kwargs):
    log = _on_instance_deleted(instance)
    log.users.add(instance.bo_ship.owner)
    log.users.add(instance.requester)
    log.save()


@receiver(post_save, sender=BookBorrowRecord,
          dispatch_uid='on_bookborrowrecord_saved')
def on_bookborrowrecord_saved(sender, instance, created, **kwargs):
    opcode = OP_ADD if created else OP_UPDATE
    log = _on_instance_saved(opcode, instance, res_bookbrw)
    log.users.add(instance.ownership.owner)
    log.users.add(instance.borrower)
    log.save()
    if created:
        news = CabinetNews(
            datetime=datetime.now(),
            lead=instance.ownership.owner,
            news=TEMPLATE_NEWS_BORROW_BOOK % (
                instance.borrower.id, 
                instance.borrower.get_nickname(),
                instance.ownership.id, 
                instance.ownership.book.title))
        news.save()
    elif instance.returned_date != None:
        news = CabinetNews(
            datetime=datetime.now(),
            lead=instance.borrower,
            news=TEMPLATE_NEWS_BOOK_RETURNED % (
                instance.ownership.id, 
                    instance.ownership.book.title,
                    instance.ownership.owner.id,
                    instance.ownership.owner.get_nickname()))
        news.save()


@receiver(post_delete, sender=BookBorrowRecord,
          dispatch_uid='on_bookborrowrecord_deleted')
def on_bookborrowrecord_deleted(sender, instance, **kwargs):
    log = _on_instance_deleted(instance)
    log.users.add(instance.ownership.owner)
    log.users.add(instance.borrower)
    log.save()
    

@receiver(post_save, sender=ExportLog, dispatch_uid='on_exportlog_saved')
def on_exportlog_saved(sender, instance, created, **kwargs):
    if not created:
        return

    if 'SERVER_SOFTWARE' in os.environ:
        from sae.taskqueue import add_task
        add_task(
            'export', 
            '/v1/task/export/', 
            payload='eid=%d' % instance.id)
        return

    print "local env: do real export task"


@receiver(post_save, sender=EmailVerify, dispatch_uid='on_emailverify_saved')
def on_emailverify_saved(sender, instance, created, **kwargs):
    if not created:
        return

    tt = Template(EMAIL_VERIFY_BODY_TEXT)
    th = Template(EMAIL_VERIFY_BODY_HTML)
    c = Context({
            "username": instance.user.get_nickname(),
            "code": instance.code})
    message = EmailMultiAlternatives(
        subject=EMAIL_VERIFY_TITLE.encode('utf-8'), 
        body=tt.render(c).encode('utf-8'),
        from_email=settings.EMAIL_HOST_USER, 
        to=[instance.email])
    message.attach_alternative(th.render(c).encode('utf-8'), "text/html")
    message.send(fail_silently=False)
