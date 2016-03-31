from django.contrib import admin

from oauth2app.models import Client, AccessToken, AccessRange

from cabinet import models


class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author', 'douban_id')
    search_fields = ('isbn',)


class BookOwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'book', 'status', 'visible', 'has_ebook', 'remark')


class BookCabinetAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'create_datetime', 'remark')


class CabinetNewsAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'lead', 'news')


class EBookRequestAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'requester', 'bo_ship')


class BookBorrowRequestAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'requester', 'bo_ship', 'planed_return_date', 
                    'status', 'remark')


class BookBorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('ownership', 'borrower', 'borrow_date', 'planed_return_date', 'returned_date')


class BookBorrowRecord2Admin(admin.ModelAdmin):
    list_display = ('ownership', 'borrower', 'borrow_date', 'returned_date', 'remark')


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'name', 'description')


class JoinRepositoryRequestAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'requester', 'repo', 'remark')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'user', 'title', 'content', 'status')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

class BookTagUseAdmin(admin.ModelAdmin):
    list_display = ('tag', 'user', 'book')

class BookOwnershipTagUseAdmin(admin.ModelAdmin):
    list_display = ('tag', 'user', 'bookown')

class SysBookTagUseAdmin(admin.ModelAdmin):
    list_display = ('tag', 'book')

class WeiboUserAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'uid', 'screen_name', 'avatar', 'user')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('following', 'remark', 'user')

admin.site.register(models.Book, BookAdmin)
admin.site.register(models.BookOwnership, BookOwnershipAdmin)
admin.site.register(models.BookCabinet, BookCabinetAdmin)
admin.site.register(models.CabinetNews, CabinetNewsAdmin)
admin.site.register(models.EBookRequest, EBookRequestAdmin)
admin.site.register(models.BookBorrowRequest, BookBorrowRequestAdmin)
admin.site.register(models.BookBorrowRecord, BookBorrowRecordAdmin)
admin.site.register(models.BookBorrowRecord2, BookBorrowRecord2Admin)
admin.site.register(models.Repository, RepositoryAdmin)
admin.site.register(models.JoinRepositoryRequest, JoinRepositoryRequestAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.BookTagUse, BookTagUseAdmin)
admin.site.register(models.BookOwnershipTagUse, BookOwnershipTagUseAdmin)
admin.site.register(models.SysBookTagUse, SysBookTagUseAdmin)
admin.site.register(models.WeiboUser, WeiboUserAdmin)
admin.site.register(models.Follow, FollowAdmin)
admin.site.register(Client)
admin.site.register(AccessToken)
admin.site.register(AccessRange)
