# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Page.admin_note'
        db.add_column(u'system_page', 'admin_note',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Part.admin_note'
        db.add_column(u'system_part', 'admin_note',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Program.admin_note'
        db.add_column(u'system_program', 'admin_note',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Page.admin_note'
        db.delete_column(u'system_page', 'admin_note')

        # Deleting field 'Part.admin_note'
        db.delete_column(u'system_part', 'admin_note')

        # Deleting field 'Program.admin_note'
        db.delete_column(u'system_program', 'admin_note')


    models = {
        u'system.page': {
            'Meta': {'object_name': 'Page'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Part']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'system.part': {
            'Meta': {'object_name': 'Part'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Program']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'system.program': {
            'Meta': {'object_name': 'Program'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['system']