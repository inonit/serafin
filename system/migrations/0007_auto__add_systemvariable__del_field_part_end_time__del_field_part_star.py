# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SystemVariable'
        db.create_table(u'system_systemvariable', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
            ('value', self.gf('jsonfield.fields.JSONField')(default=u'undefined')),
        ))
        db.send_create_signal(u'system', ['SystemVariable'])

        # Deleting field 'Part.end_time'
        db.delete_column(u'system_part', 'end_time')

        # Deleting field 'Part.start_time'
        db.delete_column(u'system_part', 'start_time')

        # Adding field 'Part.start_time_delta'
        db.add_column(u'system_part', 'start_time_delta',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Part.start_time_unit'
        db.add_column(u'system_part', 'start_time_unit',
                      self.gf('django.db.models.fields.CharField')(default=u'hours', max_length=32),
                      keep_default=False)

        # Adding field 'Part.end_time_delta'
        db.add_column(u'system_part', 'end_time_delta',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Part.end_time_unit'
        db.add_column(u'system_part', 'end_time_unit',
                      self.gf('django.db.models.fields.CharField')(default=u'hours', max_length=32),
                      keep_default=False)

        # Adding field 'Program.start_time'
        db.add_column(u'system_program', 'start_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 5, 5, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'SystemVariable'
        db.delete_table(u'system_systemvariable')

        # Adding field 'Part.end_time'
        db.add_column(u'system_part', 'end_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Part.start_time'
        db.add_column(u'system_part', 'start_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Part.start_time_delta'
        db.delete_column(u'system_part', 'start_time_delta')

        # Deleting field 'Part.start_time_unit'
        db.delete_column(u'system_part', 'start_time_unit')

        # Deleting field 'Part.end_time_delta'
        db.delete_column(u'system_part', 'end_time_delta')

        # Deleting field 'Part.end_time_unit'
        db.delete_column(u'system_part', 'end_time_unit')

        # Deleting field 'Program.start_time'
        db.delete_column(u'system_program', 'start_time')


    models = {
        u'system.page': {
            'Meta': {'object_name': 'Page'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Part']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'system.part': {
            'Meta': {'object_name': 'Part'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            'end_time_delta': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end_time_unit': ('django.db.models.fields.CharField', [], {'default': "u'hours'", 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Program']"}),
            'start_time_delta': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time_unit': ('django.db.models.fields.CharField', [], {'default': "u'hours'", 'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'system.program': {
            'Meta': {'object_name': 'Program'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'system.systemvariable': {
            'Meta': {'object_name': 'SystemVariable'},
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'value': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"})
        },
        u'system.variable': {
            'Meta': {'object_name': 'Variable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'var_type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['system']