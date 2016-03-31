# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BookOwnership.visible'
        db.add_column(u'cabinet_bookownership', 'visible',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BookOwnership.visible'
        db.delete_column(u'cabinet_bookownership', 'visible')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cabinet.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'douban_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cabinet.bookborrowrecord': {
            'Meta': {'object_name': 'BookBorrowRecord'},
            'borrow_date': ('django.db.models.fields.DateTimeField', [], {}),
            'borrower': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ownership': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.BookOwnership']"}),
            'planed_return_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'returned_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'cabinet.bookborrowrequest': {
            'Meta': {'object_name': 'BookBorrowRequest'},
            'bo_ship': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.BookOwnership']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'planed_return_date': ('django.db.models.fields.DateField', [], {}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'cabinet.bookcabinet': {
            'Meta': {'object_name': 'BookCabinet'},
            'books': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['cabinet.BookOwnership']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        u'cabinet.bookcomment': {
            'Meta': {'object_name': 'BookComment'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Book']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'cabinet.bookownership': {
            'Meta': {'object_name': 'BookOwnership'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Book']"}),
            'has_ebook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '16'}),
            'visible': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'cabinet.bookownershiptaguse': {
            'Meta': {'object_name': 'BookOwnershipTagUse'},
            'bookown': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.BookOwnership']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'cabinet.booktaguse': {
            'Meta': {'unique_together': "(('tag', 'user', 'book'),)", 'object_name': 'BookTagUse'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Book']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'cabinet.cabinetnews': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'CabinetNews'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'news': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'cabinet.ebookrequest': {
            'Meta': {'object_name': 'EBookRequest'},
            'bo_ship': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.BookOwnership']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'cabinet.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'cabinet.follow': {
            'Meta': {'unique_together': "(('following', 'user'),)", 'object_name': 'Follow'},
            'following': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follower_set'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'cabinet.joinrepositoryrequest': {
            'Meta': {'object_name': 'JoinRepositoryRequest'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Repository']"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'cabinet.repository': {
            'Meta': {'object_name': 'Repository'},
            'admin': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'managed_repos'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'joined_repos'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'cabinet.sysbooktaguse': {
            'Meta': {'object_name': 'SysBookTagUse'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Book']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cabinet.Tag']"})
        },
        u'cabinet.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'cabinet.weibouser': {
            'Meta': {'object_name': 'WeiboUser'},
            'avatar': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires_in': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'screen_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cabinet']