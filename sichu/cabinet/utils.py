# -*- coding: utf-8 -*-

import os
import json
import models
import random

from django.conf import settings
from django.db import IntegrityError

from cabinet.douban import DoubanClient


dc = DoubanClient(settings.DOUBAN_APIKEY)


def send_mail(to, subject, html):
    if 'SERVER_SOFTWARE' in os.environ:
        import sae.mail
        from sichu import sae_settings
        sae.mail.send_mail(
            ",".join(to), subject, html, 
            ("smtp.sina.com", 
             25, 
             sae_settings.EMAIL_HOST_USER, 
             sae_settings.EMAIL_HOST_PASSWORD, 
             False))
    else:
        print "debug: send mail to %s, subject is: %s, content is: %s" % (to, subject, html)


def get_book_from_cache(douban_id):
    try:
        import pylibmc
        mc = pylibmc.Client()
        cache = mc.get(douban_id)
        if cache is not None and cache.startswith('{'):
            return json.loads(cache)
        data = dc.get_book_by_id(douban_id)
        # if json load failed, then the data is invalid, this will goto ValueErrore
        book = json.loads(data)
        mc.set(douban_id, data)
        return book
    except ImportError, e:
    	return None
    except ValueError, e:
        return None
    except Exception, e:
        return None


def add_book(isbn):
    try:
        return models.Book.objects.get(isbn=isbn)
    except models.Book.DoesNotExist:
        pass

    douban_id = ""
    book = None
    try:
        book = json.loads(dc.get_book_by_isbn(isbn))
    except Exception, e:
        pass
    if book == None:
        return None

    title = book['title']['$t'] if book.has_key('title') else ""
    author = book['author'][0]['name']['$t'] if book.has_key('author') else ""
    cover = book['link'][2]['@href'] if book.has_key('link') else ""
    douban_id = book['link'][0]['@href'].split('/')[-1]    
    b = models.Book(isbn=isbn, 
                    title=title, 
                    author=author, 
                    cover=cover,
                    douban_id=douban_id)
    b.save()
    if book.has_key('db:tag'):
        try:
            b.tags = ','.join([ i['@name'] for i in book['db:tag']])
        except IntegrityError:
            pass
    return b


def get_random_books(num):
    cnt = models.Book.objects.count()
    idx = random.randint(0, cnt)
    return models.Book.objects.order_by('-id')[idx: idx + num]


def get_page_num(total, num_per_page):
    ret = divmod(total, num_per_page)
    return ret[0] + bool(ret[1])


def get_wishlist():
    wishlist = []
    try:
        wishlist = models.BookTagUse.objects.filter(
            tag = models.Tag.objects.get(name=u"想借"))
    except models.Tag.DoesNotExist:
        pass
    return wishlist


def get_from_mc(key):
    try:
        import pylibmc
        mc = pylibmc.Client()
        return mc.get(douban_id)
    except ImportError:
        pass


def delete_from_mc(key):
    try:
        import pylibmc
        mc = pylibmc.Client()
        return mc.delete(douban_id)
    except ImportError:
        pass
