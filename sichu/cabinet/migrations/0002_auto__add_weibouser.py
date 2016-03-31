# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WeiboUser'
        db.create_table('cabinet_weibouser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('screen_name', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('avatar', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('expires_in', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('cabinet', ['WeiboUser'])


    def backwards(self, orm):
        # Deleting model 'WeiboUser'
        db.delete_table('cabinet_weibouser')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cabinet.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'douban_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'cabinet.bookborrowrecord': {
            'Meta': {'object_name': 'BookBorrowRecord'},
            'borrow_date': ('django.db.models.fields.DateTimeField', [], {}),
            'borrower': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ownership': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.BookOwnership']"}),
            'planed_return_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'returned_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'cabinet.bookborrowrequest': {
            'Meta': {'object_name': 'BookBorrowRequest'},
            'bo_ship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.BookOwnership']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'planed_return_date': ('django.db.models.fields.DateField', [], {}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.bookcabinet': {
            'Meta': {'object_name': 'BookCabinet'},
            'books': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cabinet.BookOwnership']", 'null': 'True', 'blank': 'True'}),
            'create_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'cabinet.bookcomment': {
            'Meta': {'object_name': 'BookComment'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Book']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.bookownership': {
            'Meta': {'object_name': 'BookOwnership'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Book']"}),
            'has_ebook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'cabinet.bookownershiptaguse': {
            'Meta': {'object_name': 'BookOwnershipTagUse'},
            'bookown': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.BookOwnership']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.booktaguse': {
            'Meta': {'unique_together': "(('tag', 'user', 'book'),)", 'object_name': 'BookTagUse'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.cabinetnews': {
            'Meta': {'object_name': 'CabinetNews'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'news': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'cabinet.ebookrequest': {
            'Meta': {'object_name': 'EBookRequest'},
            'bo_ship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.BookOwnership']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.joinrepositoryrequest': {
            'Meta': {'object_name': 'JoinRepositoryRequest'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Repository']"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cabinet.repository': {
            'Meta': {'object_name': 'Repository'},
            'admin': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'managed_repos'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'joined_repos'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'cabinet.sysbooktaguse': {
            'Meta': {'object_name': 'SysBookTagUse'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cabinet.Tag']"})
        },
        'cabinet.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'cabinet.weibouser': {
            'Meta': {'object_name': 'WeiboUser'},
            'avatar': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires_in': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'screen_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cabinet']