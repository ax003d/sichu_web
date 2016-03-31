# -*- coding: utf-8 -*-

import logging
import sys

from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, \
    login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, \
    SetPasswordForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import logout
from django.contrib.sites.models import get_current_site
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings

from apiserver.forms import BookBorrowRequestForm
from apiserver.models import EmailVerify
from cabinet import models, utils
from cabinet.forms import PasswordResetForm, FollowForm

from weibo import APIClient, APIError
import datetime
import traceback

logger = logging.getLogger('django.request')

LATEST_BOOKS_PER_PAGE = 16
MY_BOOKS_PER_PAGE = 5
LOANED_BOOKS_PER_PAGE = 5
BORROWED_BOOKS_PER_PAGE = 5
WANTED_BOOKS_PER_PAGE = 5
WISH_BOOKS_PER_PAGE = 16

def get_weibo_client():
    return APIClient(
        app_key=settings.APP_KEY, 
        app_secret=settings.APP_SECRET, 
        redirect_uri=settings.CALLBACK_URL)

def index(request):
    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           'bookowns': models.BookOwnership.objects.filter(~Q(status=5), Q(visible=1)).order_by('-id')[:LATEST_BOOKS_PER_PAGE],
           'page_num': utils.get_page_num(models.BookOwnership.objects.filter(~Q(status=5)).count(), LATEST_BOOKS_PER_PAGE),
           }
    ctx.update(csrf(request))
    return render_to_response('cabinet/index.html', ctx)


@login_required
def mybookshelf(request):
    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.filter(~Q(status=5)).count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           'my_books': request.user.bookownership_set.filter(~Q(status=5))[:5],
           'mb_page_num': utils.get_page_num(request.user.bookownership_set.filter(~Q(status=5)).count(), 5),
           'loaned_recs': request.user.book_loaned()[:5],
           'lr_page_num': utils.get_page_num(len(request.user.book_loaned()), 5),
           'borrow_recs': request.user.bookborrowrecord_set.\
               order_by('returned_date')[:5],
           'br_page_num': utils.get_page_num(request.user.bookborrowrecord_set.count(), 5),
           'wanted_books': request.user.book_wanted()[:5],
           'wl_page_num': utils.get_page_num(request.user.book_wanted().count(), 5)
           }
    ctx.update(csrf(request))
    return render_to_response('cabinet/mybookshelf.html', ctx)


@login_required
def sys_msgs(request):
    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           'ebook_requests': request.user.ebook_requests(),
           'borrow_requests': request.user.borrow_requests(),
           'join_repo_requests': request.user.join_repo_requests()}
    ctx.update(csrf(request))    
    return render_to_response('cabinet/sys_msgs.html', ctx)


@login_required
def personal_info(request):
    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url()
           }
    ctx.update(csrf(request))
    return render_to_response('cabinet/personal_info.html', ctx) 


def book_info(request, bid):
    try:
        book = models.Book.objects.get(id=bid)
        ctx = {'user': request.user,
               'user_num': models.User.objects.count(),
               'book_num': models.BookOwnership.objects.count(),
               'borrow_num': models.BookBorrowRecord.objects.count(),
               'news': models.CabinetNews.get_latest(5),
               'actives': models.User.objects.order_by('-last_login')[:12],
               'weibo_auth': get_weibo_client().get_authorize_url(),
               'book': book}
        ctx.update(csrf(request))
        return render_to_response('cabinet/book_info.html', ctx)
    except models.Book.DoesNotExist:
        return HttpResponse("Book not found!")


def book_info_v2(request, bid):
    book = get_object_or_404(models.Book, id=bid)
    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo': get_weibo_client().get_authorize_url(),
           'book': book}
    ctx.update(csrf(request))
    return render_to_response('cabinet/book_info_v2.html', ctx)


@login_required
def chg_personal_info(request):
    results = {'success': False,
               'email_used': False}
    try:
        request.user.last_name = request.POST['last_name']
        request.user.first_name = request.POST['first_name']
        if len(models.User.objects.filter(
                Q(email=request.POST['email']),
                ~ Q(username=request.user.username))
               ) != 0:
            results['email_used'] = True
        else:
            request.user.email = request.POST['email']
        request.user.save()
        results['success'] = True
    except Exception, e:
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


@login_required
def chg_pwd(request):
    results = {'success': False,
               'old_pwd_err': False,
               'new_pwd_err': False}
    try:
        if request.user.has_usable_password() and\
                (not request.user.check_password(request.POST['old_pwd'])):
            results['old_pwd_err'] = True
        if request.POST['password1'] != request.POST['password2']:
            results['new_pwd_err'] = True
        if (not results['old_pwd_err']) and (not results['new_pwd_err']):
            request.user.set_password(request.POST['password1'])
            request.user.save()
            results['success'] = True
    except Exception, e:
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


def register(request):
    ctx = {}
    ctx.update(csrf(request))
    if request.method == 'GET':
        return render_to_response("registration/register.html", ctx)
    
    try:
        ret = {'success': False,
               'user_exist': False,
               'email_used': False}
        ctx['username'] = request.POST['username']
        ctx['email'] = request.POST['email']
        user = models.User.objects.get(username=request.POST['username'])
        ret['user_exist'] = True
    except models.User.DoesNotExist:
        if len(models.User.objects.filter(email=request.POST['email'])) != 0:
            ret['email_used'] = True
        else:
            user = models.User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password_1'])
            user.first_name = request.POST['username']
            user.save()
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password_1'])
            auth_login(request, user)
            ret['success'] = True
    except Exception, e:
        ret['message'] = str(e)
    json = simplejson.dumps(ret)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def send_test_mail(request):
    results = {'success': False}
    try:
        email = request.GET['email']
        utils.send_mail([email],
                        u"测试邮件",
                        u"This is a test email from sichu.sinaapp.com!")
        results['success'] = True
    except Exception, e:
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


@login_required
def add_book(request):
    if request.method == 'GET':
        raise Http404
    results = {'success': False}
    try:
        b = utils.add_book(request.POST['isbn'])
        if b == None:
            results['message'] = u"无法找到ISBN为 %s 的书籍信息!" % request.POST['isbn']
        else:
            bo = models.BookOwnership(
                owner=request.user,
                book=b,
                status=request.POST['status'],
                has_ebook=request.POST['has_ebook'] == '1',
                visible=request.POST.get('visible'),
                remark=request.POST['remark'])
            bo.save()
            results['success'] = True
    except Exception, e:
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


def show_user(request, uid):
    try:
        user = models.User.objects.get(id=uid)        
        ctx = {'user': user,
               'user_num': models.User.objects.count(),
               'book_num': models.BookOwnership.objects.count(),
               'borrow_num': models.BookBorrowRecord.objects.count(),
               'news': models.CabinetNews.get_user_latest(user, 5),
               'actives': models.User.objects.order_by('-last_login')[:12],
               'weibo_auth': get_weibo_client().get_authorize_url(),
               'bookowns': user.book_available(request.user)[:LATEST_BOOKS_PER_PAGE],
               'mb_page_num': utils.get_page_num(user.book_available().count(),
                                              LATEST_BOOKS_PER_PAGE),
               'userwanted': user.book_wanted()[:WISH_BOOKS_PER_PAGE],
               'wl_page_num': utils.get_page_num(user.book_wanted().count(),
                                                 WISH_BOOKS_PER_PAGE)
               }
        try:
            if request.user.is_anonymous():
                ctx['is_login'] = False
            else:
                ctx['is_login'] = True
                follow = request.user.follow_set.get(following=user)
                ctx['remark'] = follow.remark
        except models.Follow.DoesNotExist:
            pass
        return render_to_response('cabinet/user_info.html', ctx)
    except models.User.DoesNotExist:
        return HttpResponse("User not found!")


def show_user_v2(request, uid):
    user = get_object_or_404(models.User, id=uid)

    ctx = {'user': user,
           'news': models.CabinetNews.get_user_latest(user, 5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           'bookowns': user.book_available()[:LATEST_BOOKS_PER_PAGE],
           'mb_page_num': utils.get_page_num(user.book_available().count(),
                                             LATEST_BOOKS_PER_PAGE),
           'userwanted': user.book_wanted()[:WISH_BOOKS_PER_PAGE],
           'wl_page_num': utils.get_page_num(user.book_wanted().count(),
                                             WISH_BOOKS_PER_PAGE)
           }
    try:
        if request.user.is_authenticated():
            follow = request.user.follow_set.get(following=user)
            ctx['follow'] = follow
    except models.Follow.DoesNotExist:
        pass
    return render_to_response('cabinet/user_info_v2.html', ctx)
        

@login_required
def show_bookownership(request, boid):
    try:
        bo = models.BookOwnership.objects.get(id=boid)
        return HttpResponseRedirect('/cabinet/book/%s/' % bo.book.id)
    except models.BookOwnership.DoesNotExist:
        return HttpResponse("BookOwnership not found!")


@login_required
def edit_bookownership(request):
    results = {'success': False}
    try:
        bo = models.BookOwnership.objects.get(id=request.POST['bookownership'])
        if bo.owner != request.user:
            json = simplejson.dumps(results)
            return HttpResponse(json, mimetype='application/json')
        
        visible = request.POST.get('visible')
        bo.status = request.POST['status']
        bo.has_ebook = request.POST['has_ebook'] == '1'
        if visible is not None:
            bo.visible = visible
        bo.remark = request.POST['remark']
        bo.save()
        results['success'] = True
    except models.BookOwnership.DoesNotExist:
        results['message'] = "BookOwnership not found!"
    except Exception, e:
        traceback.print_exc()
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def del_bookownership(request):
    results = {'success': False}
    try:
        bo = models.BookOwnership.objects.get(id=request.POST['bookownership'])
        if bo.owner != request.user:
            json = simplejson.dumps(results)
            return HttpResponse(json, mimetype='application/json')
        results['id'] = bo.id
        bo.delete()
        results['success'] = True
    except models.BookOwnership.DoesNotExist:
        results['message'] = "BookOwnership not found!"
    except Exception, e:
        traceback.print_exc()
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def ebook_request(request):
    results = {'success': False}
    try:
        bo = models.BookOwnership.objects.get(id=request.POST['bo_id'])
        if len(models.EBookRequest.objects.filter(
                requester=request.user, bo_ship=bo)) != 0:
            results['success'] = True
        else:
            er = models.EBookRequest(datetime=datetime.datetime.now(),
                                     requester=request.user,
                                     bo_ship=bo)
            er.save()
            utils.send_mail(
                [bo.owner.email],
                u"[私橱网]书籍电子版请求",
                u"%s 向您请求 %s 的电子版!" % (request.user.full_name(),
                                               bo.book.title))
            results['success'] = True
    except models.BookOwnership.DoesNotExist:
        results['message'] = "BookOwnership not found!"
    except Exception, e:
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def get_dlg(request):
    ctx = {}
    ctx.update(csrf(request))
    try:
        return render_to_response('cabinet/%s.html' % request.GET['dlg_type'], ctx)
    except:
        return HttpResponse("dlg not found!")


@login_required
def borrow_request(request):
    results = {'success': False}
    if str(datetime.datetime.now()) > request.POST['planed_return_date']:
        results['message'] = u"预计归还日期不能早于当天!"
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')

    try:
        bo_ship = request.POST.get('bo_ship')
        if len(models.BookBorrowRequest.objects.filter(
                bo_ship=bo_ship, 
                requester=request.user, 
                status=0)) != 0:
            results['success'] = True
        else:
            request.POST = request.POST.copy()
            request.POST['requester'] = request.user.id
            form = BookBorrowRequestForm(request.POST)
            if not form.is_valid():
                results['message'] = form.errors
            else:
                bbr = form.save()
                results['success'] = True
    except models.BookOwnership.DoesNotExist:
        results['message'] = u"未找到该书!"
    except Exception, e:
        # results['message'] = u"借阅请求失败!"
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def borrow_accept(request):
    results = {'success': False}
    try:
        bbr = models.BookBorrowRequest.objects.get(id=request.POST['brid'])
        if bbr.bo_ship.owner != request.user:
            results['message'] = u"非该书拥有者, 不能操作该书!"
            json = simplejson.dumps(results)
            return HttpResponse(json, mimetype='application/json')

        if bbr.status != 0:
            # request had been processed
            results['success'] = True
            json = simplejson.dumps(results)
            return HttpResponse(json, mimetype='application/json')

        if request.POST['accepted'] == "1":
            # request accepted
            if bbr.bo_ship.status != u"1":
                results['message'] = u"该书处于不可借状态!"
                json = simplejson.dumps(results)
                return HttpResponse(json, mimetype='application/json')
            bbr.status = 1
            bbr.save()
        else:
            # request rejected
            bbr.status = 2
            bbr.save()
        results['success'] = True
    except models.BookBorrowRequest.DoesNotExist:
        results['message'] = u"借阅请求已过期!"
    except Exception, e:
        logger.exception(str(sys._getframe().f_code.co_name))
        results['message'] = u"处理借阅请求失败!"
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def del_ebook_request(request):
    results = {'success': False}
    try:
        erq = models.EBookRequest.objects.get(id=request.POST['eqid'])
        if erq.bo_ship.owner != request.user:
            results['message'] = u"非该请求所有者，不能删除该请求!"
        else:
            erq.delete()
            results['success'] = True
    except models.EBookRequest.DoesNotExist:
        results['message'] = u"请求已过期!"
    except Exception, e:
        results['message'] = u"删除请求失败!"
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')        


@login_required
def return_book(request):
    results = {'success': False}
    try:
        bbr = models.BookBorrowRecord.objects.get(id=request.POST['br_id'])
        if bbr.ownership.owner != request.user:
            results['message'] = u"非该书主人, 不能操作该书!"
            json = simplejson.dumps(results)
            return HttpResponse(json, mimetype='application/json')
        bbr.returned_date = datetime.datetime.now()
        bbr.save()
        bbr.ownership.status = u"1"
        bbr.ownership.save()
        results['success'] = True
        results['id'] = bbr.id
        results['date'] = bbr.returned_date.isoformat()
    except models.BookBorrowRecord.DoesNotExist:
        results['message'] = "BookBorrowRecord not found!"
    except Exception, e:
        results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


def search(request):
    books = None
    keyword = request.GET.get('keyword')
    if keyword == u"ISBN/书名/作者":
        keyword = None
    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           'keyword': keyword,
           'books': books
        }
    if keyword is None:
        ctx['keyword'] = ''
        ctx.update(csrf(request))
        return render_to_response('cabinet/search_results.html', ctx)

    # search by isbn
    if keyword.isdigit():
        books = utils.add_book(keyword)
    # search by title/author
    if books == None:
        books = models.Book.objects.filter(
            Q(title__icontains=keyword) | 
            Q(author__icontains=keyword))
    else:
        books = [books]

    ctx['books'] = books
    ctx.update(csrf(request))
    return render_to_response('cabinet/search_results.html', ctx)


@login_required
def repos(request):
    ctx = {'repos': request.user.joined_repos.all()}
    return render_to_response('cabinet/repos.html', ctx)


@login_required
def other_repos(request):
    ctx = {'applies': request.user.joinrepositoryrequest_set.all(),
           'repos': set(models.Repository.objects.all()) - set(request.user.joined_repos.all()) - set([jrr.repo for jrr in request.user.joinrepositoryrequest_set.all()])}
    return render_to_response('cabinet/other_repos.html', ctx)


@login_required
def create_repo(request):
    results = {'success': False}
    try:
        name = request.POST['name']
        description = request.POST['description']
        # verify input
        if len(request.user.managed_repos.all()) > 9:
            results['message'] = u"创建公馆失败,您管理的小组不能超过10个!"
        else:
            repo = models.Repository(create_time=datetime.datetime.now(),
                                     name=name,
                                     description=description)
            repo.save()
            repo.admin.add(request.user)
            repo.members.add(request.user)
            repo.save()
            results['success'] = True
    except Exception, e:
        results['message'] = u"创建公馆失败!"
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


@login_required
def repo_apply(request):
    results = {'success': False}
    try:
        repo = models.Repository.objects.get(id=request.POST['repo_id'])
        if request.user in repo.members.all():
            results['message'] = u"您已经是该公馆成员!"
        elif len(request.user.joinrepositoryrequest_set.filter(repo=repo)) != 0:
            results['message'] = u"请勿重复提交申请!"
        else:
            rqt = models.JoinRepositoryRequest(
                datetime=datetime.datetime.now(),
                requester=request.user,
                repo=repo,
                remark=request.POST['remark'])
            rqt.save()
            utils.send_mail(
                [ u.email for u in repo.admin.all()],
                u"[私橱网]加入公馆请求",
                u"%s 申请加入%s公馆 备注：%s" % (
                    request.user.full_name(), repo.name, request.POST['remark']))
            results['success'] = True
    except models.Repository.DoesNotExist:
        results['message'] = u"未找到该公馆!"
    except Exception, e:
        results['message'] = u"申请加入公馆失败!"
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def join_repo_process(request):
    results = {'success': False}
    try:
        jrr = models.JoinRepositoryRequest.objects.get(id=request.POST['jr_id'])
        if request.user not in jrr.repo.admin.all():
            results['message'] = u"您不是该公馆的管理员，不能处理该请求!"
        elif request.POST['accepted'] == "1":
            if jrr.requester not in jrr.repo.members.all():
                jrr.repo.members.add(jrr.requester)
                results['success'] = True
                utils.send_mail(
                    [jrr.requester.email],
                    u"[私橱网]成功加入公馆",
                    u"管理员%s同意您加入%s公馆!" % (
                        request.user.full_name(), jrr.repo.name))
            else:
                results['success'] = True
            jrr.delete()
        elif request.POST['accepted'] == "0":
            jrr.delete()
            results['success'] = True
    except models.JoinRepositoryRequest.DoesNotExist:
        results['success'] = True
        # results['message'] = u"该请求已经处理!"
    except Exception, e:        
        results['message'] = u"处理加入公馆请求失败!"
        # results['message'] = str(e)
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')    


@login_required
def show_repo(request, rid):
    try:
        repo = models.Repository.objects.get(id=rid)
        if request.user not in repo.members.all():
            return HttpResponse(u"您不是该公馆成员,不能查看公馆详细信息!")
        ctx = {'repo': repo}
        return render_to_response('cabinet/repo_info.html', ctx)
    except models.Repository.DoesNotExist:
        return HttpResponse(u"未发现该公馆")


def books_get_page(request, page, page_num, type, ver=1):
    page = int(page)
    if page <= 1:
        page = 0
    elif page >= page_num:
        page = page_num - 1
    else:
        page -= 1
    ctx = {'page': page + 1, 'type': type, 'ver': ver}
    if type == "latest":
        ctx['bookowns'] = models.BookOwnership.objects.\
            order_by('-id')[
            LATEST_BOOKS_PER_PAGE * page : LATEST_BOOKS_PER_PAGE * (page + 1)]
    elif type == "mybooks":
        ctx['my_books'] = request.user.bookownership_set.all()[
            MY_BOOKS_PER_PAGE * page : MY_BOOKS_PER_PAGE * (page + 1)]
    elif type == "loaned":
        ctx['loaned_recs'] = request.user.book_loaned()[
            LOANED_BOOKS_PER_PAGE * page : LOANED_BOOKS_PER_PAGE * (page + 1)]
    elif type == "borrowed":
        ctx['borrow_recs'] = request.user.bookborrowrecord_set.\
            order_by('returned_date')[
            BORROWED_BOOKS_PER_PAGE * page : BORROWED_BOOKS_PER_PAGE * (page + 1)]
    elif type == "wanted":
        ctx['wanted_books'] = request.user.book_wanted()[
            WANTED_BOOKS_PER_PAGE * page : WANTED_BOOKS_PER_PAGE * (page + 1)]
    elif type == "wish":
        ctx['wishlist'] = utils.get_wishlist()[
            WISH_BOOKS_PER_PAGE * page : WISH_BOOKS_PER_PAGE * (page + 1)]
    elif type.startswith("userbook"):
        uid = type.split('_')[1]
        user = models.User.objects.get(id=uid)
        ctx['bookowns'] = user.book_available()[
            LATEST_BOOKS_PER_PAGE * page : LATEST_BOOKS_PER_PAGE * (page + 1)]
    elif type.startswith("userwanted"):
        uid = type.split('_')[1]
        user = models.User.objects.get(id=uid)
        ctx['userwanted'] = user.book_wanted()[
            WISH_BOOKS_PER_PAGE * page : WISH_BOOKS_PER_PAGE * (page + 1)]
    ctx.update(csrf(request))
    return render_to_response('cabinet/page_books.html', ctx)


def books_latest(request, page):
    page_num = utils.get_page_num(models.BookOwnership.objects.count(), LATEST_BOOKS_PER_PAGE)
    return books_get_page(request, page, page_num, 'latest')


@login_required
def books_mybooks(request, page):
    page_num = utils.get_page_num(request.user.bookownership_set.count(), 5)
    return books_get_page(request, page, page_num, 'mybooks')


def books_loaned(request, page):
    page_num = utils.get_page_num(len(request.user.book_loaned()), 5)
    return books_get_page(request, page, page_num, 'loaned')


def books_borrowed(request, page):
    page_num = utils.get_page_num(request.user.bookborrowrecord_set.count(), 5)
    return books_get_page(request, page, page_num, 'borrowed')


def books_wanted(request, page):
    page_num = utils.get_page_num(len(request.user.book_wanted()), 5)
    return books_get_page(request, page, page_num, 'wanted')    


def books_wish(request, page):
    page_num = utils.get_page_num(utils.get_wishlist().count(), 5)
    return books_get_page(request, page, page_num, 'wish')


def userbook(request, uid, page):
    user = models.User.objects.get(id=uid)
    page_num = utils.get_page_num(user.book_available().count(),
                                  LATEST_BOOKS_PER_PAGE)
    return books_get_page(request, page, page_num, 'userbook_' + uid)


def userbook_v2(request, uid, page):
    user = models.User.objects.get(id=uid)
    page_num = utils.get_page_num(user.book_available().count(),
                                  LATEST_BOOKS_PER_PAGE)
    return books_get_page(request, page, page_num, 'userbook_' + uid, 2)


def userwanted(request, uid, page):
    user = models.User.objects.get(id=uid)
    page_num = utils.get_page_num(len(user.book_wanted()),
                                  WANTED_BOOKS_PER_PAGE)
    return books_get_page(request, page, page_num, 'userwanted_' + uid)


def userwanted_v2(request, uid, page):
    user = models.User.objects.get(id=uid)
    page_num = utils.get_page_num(len(user.book_wanted()),
                                  WANTED_BOOKS_PER_PAGE)
    return books_get_page(request, page, page_num, 'userwanted_' + uid, 2)


@login_required
def book_want(request):
    ret = {'result': False}
    
    tag = None
    try:
        tag = models.Tag.objects.get(name=u"想借")
    except models.Tag.DoesNotExist:
        tag = models.Tag(name=u"想借")
        tag.save()

    book = None
    try:
        book = models.Book.objects.get(id=request.POST.get('book_id'))
    except models.Book.DoesNotExist:
        ret['message'] = "Book does not exist"
        json = simplejson.dumps(ret)
        return HttpResponse(json, mimetype='application/json')

    try:
        btu = models.BookTagUse(tag=tag, user=request.user, book=book)
        btu.save()
        ret['result'] = True
    except IntegrityError:
        ret['message'] = "You have tagged this book as want!"
    
    json = simplejson.dumps(ret)
    return HttpResponse(json, mimetype='application/json')


@login_required
def check_isbn(request):
    book = utils.add_book(request.GET['isbn'])
    if book == None:
        return HttpResponse(u"无法找到该书!")
    else:
        return render_to_response('cabinet/check_book.html', {'book': book})


@login_required
def del_bookwant(request):
    results = {'success': False}
    wt_id = request.POST.get('wt_id')
    if wt_id is None:
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype='application/json')
    try:
        btu = models.BookTagUse.objects.get(id=wt_id)
        if btu.user == request.user:
            results['id'] = btu.id
            btu.delete()
            results['success'] = True
    except models.BookTagUse.DoesNotExist:
        pass
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


def wishlist(request):
    wishlist = models.BookTagUse.objects.get_empty_query_set()
    try:
        wishlist = models.BookTagUse.objects.filter(
            tag=models.Tag.objects.get(name=u"想借"))
    except models.Tag.DoesNotExist:
        pass

    ctx = {'user': request.user,
           'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           'wishlist': wishlist[:LATEST_BOOKS_PER_PAGE],
           'page_num': utils.get_page_num(wishlist.count(), LATEST_BOOKS_PER_PAGE)
           }
    ctx.update(csrf(request))
    return render_to_response('cabinet/wishlist.html', ctx)


# 4 views for password reset:
# - password_reset sends the mail
# - password_reset_done shows a success message for the above
# - password_reset_confirm checks the link the user clicked and
#   prompts for a new password
# - password_reset_complete shows a success message for the above

@csrf_protect
def password_reset(request, is_admin_site=False, template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        password_reset_form=PasswordResetForm, token_generator=default_token_generator,
        post_reset_redirect=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_done')
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {}
            opts['use_https'] = request.is_secure()
            opts['token_generator'] = token_generator
            opts['email_template_name'] = email_template_name
            opts['request'] = request
            if is_admin_site:
                opts['domain_override'] = request.META['HTTP_HOST']
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    if request.user.username:
        return HttpResponseRedirect('/cabinet/index/')

    """Displays the login form and handles the login action."""
    redirect_to = request.REQUEST.get(redirect_field_name, '')        

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'books': utils.get_random_books(18),
        'weibo': get_weibo_client().get_authorize_url()
    }, context_instance=RequestContext(request))


def sc_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def callback_weibo_auth(request):
    code = request.GET.get('code')
    if code is None:
        # access token got by mobile app, so we ignore it here
        return HttpResponse('Got it!')

    wc = get_weibo_client()
    try:
        token = wc.request_access_token(code)
    except APIError, e:
        if e.error_code != 21325:
            logger.exception(str(sys._getframe().f_code.co_name))
        raise e
    wc.set_access_token(token.access_token, token.expires_in)
    us = wc.get.users__show(uid=token.uid)

    # if weibo user not exist
    #   create weibo user do not bind
    wu = None
    try:
        wu = models.WeiboUser.objects.get(uid=us.id)
        wu.update(us.screen_name, 
                  us.profile_image_url, 
                  token.access_token, 
                  token.expires_in)
    except models.WeiboUser.DoesNotExist:
        wu = models.WeiboUser(uid=us.id,
                              screen_name=us.screen_name,
                              avatar=us.profile_image_url,
                              token=token.access_token,
                              expires_in=token.expires_in)
        wu.save()

    # if user already login, bind weibo to this user    
    # return
    if not request.user.is_anonymous():
        wu.user = request.user
        wu.save()
        return HttpResponseRedirect('/cabinet/index/')        

    # if weibo user bind to a user
    #   login
    # else
    #   create a default user & login
    if wu.user is None:
        user, create = models.User.objects.get_or_create(username=us.id)
        if create:
            user.first_name = us.screen_name
            user.save()
        wu.user = user
        wu.save()

    user = authenticate(wid=wu.uid)
    auth_login(request, user)
    return HttpResponseRedirect('/cabinet/index/')


@login_required
@csrf_exempt
def following(request):
    ret = {'success': False}
    if request.method != 'POST':
        json = simplejson.dumps(ret)
        return HttpResponse(json, mimetype='application/json')

    request.POST = request.POST.copy()
    request.POST['user'] = request.user.id
    form = FollowForm(request.POST)
    if not form.is_valid():
        ret['message'] = form.errors
    else:
        f = form.save()
        ret['success'] = True
        ret['id'] = f.id

    json = simplejson.dumps(ret)
    return HttpResponse(json, mimetype='application/json')


@login_required
@csrf_exempt
def following_del(request):
    ret = {'success': False}

    try:
        f = models.Follow.objects.get(id=request.POST.get('id'))
        if f.user == request.user:
            f.delete()
            ret['success'] = True
    except models.Follow.DoesNotExist:
        pass

    json = simplejson.dumps(ret)
    return HttpResponse(json, mimetype='application/json')


@login_required
def friends(request):
    ctx = {'user_num': models.User.objects.count(),
           'book_num': models.BookOwnership.objects.\
               filter(~Q(status=5)).count(),
           'borrow_num': models.BookBorrowRecord.objects.count(),
           'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo_auth': get_weibo_client().get_authorize_url(),
           }
    return render_to_response('cabinet/friends.html', ctx,
                              RequestContext(request))


def help(request):
    ctx = {'news': models.CabinetNews.get_latest(5),
           'actives': models.User.objects.order_by('-last_login')[:12],
           'weibo': get_weibo_client().get_authorize_url()}
    return render_to_response('cabinet/help.html', ctx,
                              RequestContext(request))


def email_verify(request):
    verified = False
    code = request.GET.get('code')
    try:
        ev = get_object_or_404(EmailVerify, code=code)
        if ev.verified == False:
            ev.verified = True
            ev.save()
            ev.user.email = ev.email
            ev.user.save()
            verified = True
    except Http404:
        pass

    if verified:
        return render_to_response('cabinet/email_verify_ok.html', {})
    return render_to_response('cabinet/email_verify_error.html', {})
        


@login_required
def monitor__mc(request):
    if not request.user.is_superuser:
        return HttpResponse('Not permit!')
    douban_id = str(request.GET.get('douban_id'))
    delete = request.GET.get('delete')
    cache = utils.get_from_mc(douban_id)
    if cache is None:
        return HttpResponse('%s not in memcached!' % douban_id)
    if delete == '1':
        utils.delete_from_mc(douban_id)
        return HttpResponse('%s deleted in memcached!' % douban_id)
    return HttpResponse(cache)
