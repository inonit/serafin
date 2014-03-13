# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Page.data'
        db.add_column(u'system_page', 'data',
                      self.gf('jsonfield.fields.JSONField')(default=u'[{}]'),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Page.data'
        db.delete_column(u'system_page', 'data')


    models = {
        u'system.page': {
            'Meta': {'object_name': 'Page'},
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'[{}]'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'system.part': {
            'Meta': {'object_name': 'Part'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Program']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'system.program': {
            'Meta': {'object_name': 'Program'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['system']