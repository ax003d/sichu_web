# -*- coding: utf-8 -*- 

import logging
import pdb
import datetime
import tagging

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db.models import Q

from cabinet import utils
from gravatar.templatetags.gravatar import gravatar_for_email

logger = logging.getLogger('django.request')

class Book(models.Model):
    isbn = models.CharField(max_length=100, verbose_name='ISBN')
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.URLField(blank=True)
    douban_id = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.title

    def get_image_url(self):
        book = None
        if len(self.tags) == 0:
            book = utils.get_book_from_cache(str(self.douban_id))
            try:
                self.tags = ','.join([ i['@name'] for i in book['db:tag']])
            except IntegrityError:
                pass
            except TypeError:
                pass
        if self.cover == "":
            if book is None:
                book = utils.get_book_from_cache(str(self.douban_id))
            if book is None:
                return self.cover
            self.cover = book['link'][2]['@href']
            self.save()
        return self.cover.replace('spic', 'lpic')
    
    def available_bookownership(self):
        return self.bookownership_set.filter(~Q(status=u"5"))

tagging.register(Book)


class BookComment(models.Model):
    datetime = models.DateTimeField()
    book = models.ForeignKey(Book)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=256)    
    content = models.CharField(max_length=2048)
    status = models.IntegerField()


BO_STAT = (
    ("1", "可借"),
    ("2", "不可借"),
    ("3", "借出"),
    ("4", "丢失"),
    ("5", "删除"))

BO_VISIBLE = (
    (1, u'所有人'),
    (2, u'好友可见'),
    (3, u'仅自己可见')
)

class BookOwnership(models.Model):
    owner  = models.ForeignKey(User)
    book   = models.ForeignKey(Book)
    status = models.CharField(max_length=16, 
                              choices=BO_STAT, 
                              default='1')
    has_ebook = models.BooleanField()
    visible = models.IntegerField(choices=BO_VISIBLE, default=1)
    remark = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return self.owner.username + "-" + self.book.title

    def ebook_requests(self):
        return self.ebookrequest_set.all()

    def borrow_requests(self):
        return self.bookborrowrequest_set.all().order_by('status')

    def borrow_records(self):
        return self.bookborrowrecord_set.all()

    @staticmethod
    def available(self):
        return self.objects.filter(~Q(status="5"))


class BookBorrowRecord(models.Model):    
    ownership = models.ForeignKey(BookOwnership)
    borrower = models.ForeignKey(User)
    borrow_date = models.DateTimeField()
    planed_return_date = models.DateField(blank=True)
    returned_date = models.DateTimeField(blank=True, null=True)


class BookBorrowRecord2(models.Model):    
    ownership = models.ForeignKey(BookOwnership)
    borrower = models.CharField(max_length=64)
    borrow_date = models.DateTimeField()
    returned_date = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=256, blank=True)


class BookCabinet(models.Model):
    owner = models.ForeignKey(User)
    name  = models.CharField(max_length=100)
    create_datetime = models.DateTimeField()
    remark = models.CharField(max_length=256, blank=True)
    books = models.ManyToManyField(BookOwnership, blank=True, null=True)

    def __unicode__(self):
        return self.owner.username + "-" + self.name


class CabinetNews(models.Model):
    datetime = models.DateTimeField()
    lead = models.ForeignKey(User)
    news = models.CharField(max_length=256)

    class Meta:
        ordering = ['-datetime']

    def __unicode__(self):
        return str(self.datetime) + "-" + self.lead.username

    @staticmethod
    def get_latest(num):
        return CabinetNews.objects.all().order_by('-datetime')[:num]

    @staticmethod
    def get_user_latest(user, num):
        return CabinetNews.objects.filter(lead=user).order_by('-datetime')[:num]

REQ_STATUS = (
    (0, u'未处理'),
    (1, u'已同意'),
    (2, u'已拒绝'),
    )

class EBookRequest(models.Model):
    datetime  = models.DateTimeField()
    requester = models.ForeignKey(User)
    bo_ship   = models.ForeignKey(BookOwnership)
    status    = models.IntegerField(choices=REQ_STATUS, default=0)
    
    def __unicode__(self):
        return str(self.datetime) + "-" + self.requester.username


class BookBorrowRequest(models.Model):
    datetime  = models.DateTimeField(auto_now_add=True)
    requester = models.ForeignKey(User)
    bo_ship   = models.ForeignKey(BookOwnership)
    planed_return_date = models.DateField()
    remark    = models.CharField(max_length=256, blank=True)
    status    = models.IntegerField(choices=REQ_STATUS, default=0)

    def __unicode__(self):
        return str(self.datetime) + "-" + self.requester.username


def book_num(self):
    return self.bookownership_set.filter(~Q(status="5")).count()

setattr(User, 'book_num', book_num)


def sorted_recs(rec_a, rec_b):
    if rec_a.returned_date is None:
        return -1
    if rec_b.returned_date is None:
        return 1
    return (1 if rec_a.returned_date < rec_b.returned_date else -1)


def book_loaned(self):
    brs = [ bo.borrow_records() for bo in self.bookownership_set.all()]
    loaned_recs = self.bookownership_set.get_empty_query_set()
    if len(brs) != 0:        
        loaned_recs = reduce(QuerySet.__or__, brs)
    return sorted(loaned_recs, sorted_recs)

setattr(User, 'book_loaned', book_loaned)


def book_wanted(self):
    wishlist = BookTagUse.objects.get_empty_query_set()
    try:
        wishlist = BookTagUse.objects.filter(
            tag=Tag.objects.get(name=u"想借"),
            user=self)
    except Tag.DoesNotExist:
        pass
    return wishlist

setattr(User, 'book_wanted', book_wanted)    


def full_name(self):
    return (self.last_name + self.first_name)

setattr(User, 'full_name', full_name)


def ebook_requests(self):
    ers = [ bo.ebook_requests() for bo in self.bookownership_set.all()]
    ebook_requests = EBookRequest.objects.get_empty_query_set()
    if len(ers) != 0:
        ebook_requests = reduce(QuerySet.__or__, ers)
    return ebook_requests

setattr(User, 'ebook_requests', ebook_requests)


def borrow_requests(self):
    brs = [ bo.borrow_requests() for bo in self.bookownership_set.all()]
    borrow_requests = BookBorrowRequest.objects.get_empty_query_set()
    if len(brs) != 0:
        borrow_requests = reduce(QuerySet.__or__, brs)
    return borrow_requests

setattr(User, 'borrow_requests', borrow_requests)


def book_available(self, user=None):
    query = ~Q(status="5")
    if (user is not None) and user.is_authenticated() and self.is_following(user):
        query &= Q(visible__lte=2)
    else:
        query &= Q(visible=1)
    return self.bookownership_set.filter(query)

setattr(User, 'book_available', book_available)


def message_num(self):
    return self.borrow_requests().filter(status=0).count() + \
        self.ebook_requests().count() + \
        self.join_repo_requests().count()

setattr(User, 'message_num', message_num)


def join_repo_requests(self):
    jrrs = [ r.join_requests() for r in self.managed_repos.all() ]
    join_repo_requests = JoinRepositoryRequest.objects.get_empty_query_set()
    if len(jrrs) != 0:
        join_repo_requests = reduce(QuerySet.__or__, jrrs)
    return join_repo_requests

setattr(User, 'join_repo_requests', join_repo_requests)


class Repository(models.Model):
    create_time = models.DateTimeField()
    admin = models.ManyToManyField(User, related_name="managed_repos")
    members = models.ManyToManyField(User, related_name="joined_repos")
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1024, blank=True)

    def __unicode__(self):
        return self.name

    def book_num(self):
        total = 0
        for m in self.members.all():
            total += m.bookownership_set.count()
        return total

    def join_requests(self):
        return self.joinrepositoryrequest_set.all()

    def total_loaned_times(self):
        total = 0
        for m in self.members.all():
            total += m.book_loaned().count()
        return total

    def total_borrowed_times(self):
        total = 0
        for m in self.members.all():
            total += m.bookborrowrecord_set.count()
        return total

    def all_books(self):
        bs = [ m.bookownership_set.all() for m in self.members.all() ]
        books = BookOwnership.objects.get_empty_query_set()
        if len(bs) != 0:
            books = reduce(QuerySet.__or__, bs)
        return books

    def get_latest_news(self, num=100):
        ns = [ m.cabinetnews_set.all() for m in self.members.all() ]
        news = CabinetNews.objects.get_empty_query_set()
        if len(ns) != 0:
            news = reduce(QuerySet.__or__, ns)
        return news.order_by('-datetime')[:num]


class JoinRepositoryRequest(models.Model):
    datetime = models.DateTimeField()
    requester = models.ForeignKey(User)
    repo = models.ForeignKey(Repository)
    remark = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return self.requester.full_name() + "-" + self.repo.name


class Feedback(models.Model):
    datetime = models.DateTimeField()
    user = models.ForeignKey(User)
    title = models.CharField(max_length=256)
    content = models.CharField(max_length=1024)
    status = models.IntegerField()


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.name


class BookTagUse(models.Model):
    """
    User book classification.
    """
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)

    class Meta:
        unique_together = (('tag', 'user', 'book'),)

    def __unicode__(self):
        return self.tag.name + "-" + self.user.username + "-" + self.book.title
    

class BookOwnershipTagUse(models.Model):
    """
    BookOwnership classification.
    """
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey(User)
    bookown = models.ForeignKey(BookOwnership)


class SysBookTagUse(models.Model):
    """
    System book classification.
    """
    tag = models.ForeignKey(Tag)
    book = models.ForeignKey(Book)

    def __unicode__(self):
        return self.tag.name + "-" + self.book.title


class WeiboUser(models.Model):
    created_at  = models.DateTimeField(auto_now_add=True)
    uid         = models.CharField(max_length=16)
    screen_name = models.CharField(max_length=32, blank=True)
    avatar      = models.CharField(max_length=128, blank=True)
    token       = models.CharField(max_length=32)
    expires_in  = models.BigIntegerField()
    user        = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.screen_name

    def update(self, screen_name, avatar, token, expires_in):
        self.screen_name = screen_name
        self.avatar = avatar
        self.token = token
        self.expires_in = expires_in
        self.save()


def get_weibo(self):
    if self.weibouser_set.count() > 0:
        return self.weibouser_set.all()[0]
    return None

setattr(User, 'get_weibo', get_weibo)    


def get_nickname(self):
    full_name = self.full_name()
    if len(full_name) > 0:
        return full_name
    weibo = self.get_weibo()
    if weibo is not None:
        return weibo.screen_name
    return self.username

setattr(User, 'get_nickname', get_nickname)


def get_avatar(self):
    weibo = self.get_weibo()
    if (weibo is not None) and (weibo.avatar is not None) and (len(weibo.avatar) > 0):
        return weibo.avatar
    try:
        return gravatar_for_email(self.email.encode('utf-8'))
    except Exception, e:
        logger.exception(self.username + ' get_avtar error ')
        return ''
    
setattr(User, 'get_avatar', get_avatar)


def get_verified_email(self):
    evs = self.emailverify_set.filter(verified=True).order_by('-updated_at')
    if len(evs) > 0:
        return evs[0].email
    return ""

setattr(User, 'get_verified_email', get_verified_email)

class Follow(models.Model):
    following = models.ForeignKey(User, related_name='follower_set')
    remark    = models.CharField(max_length=32)
    user      = models.ForeignKey(User)

    class Meta:
        unique_together = ('following', 'user')

    def __unicode__(self):
        return str(self.user) + '->' + str(self.following)


def is_following(self, user):
    try:
        Follow.objects.get(following=user, user=self)
        return True
    except Follow.DoesNotExist:
        return False
    
setattr(User, 'is_following', is_following)
