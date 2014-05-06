# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Email'
        db.create_table(u'system_email', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['system.Page'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'system', ['Email'])

        # Adding model 'SMS'
        db.create_table(u'system_sms', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['system.Page'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'system', ['SMS'])

        # Removing M2M table for field parts on 'Page'
        db.delete_table(db.shorten_name(u'system_page_parts'))


    def backwards(self, orm):
        # Deleting model 'Email'
        db.delete_table(u'system_email')

        # Deleting model 'SMS'
        db.delete_table(u'system_sms')

        # Adding M2M table for field parts on 'Page'
        m2m_table_name = db.shorten_name(u'system_page_parts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm[u'system.page'], null=False)),
            ('part', models.ForeignKey(orm[u'system.part'], null=False))
        ))
        db.create_unique(m2m_table_name, ['page_id', 'part_id'])


    models = {
        u'system.email': {
            'Meta': {'object_name': 'Email'},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['system.Page']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'system.page': {
            'Meta': {'object_name': 'Page'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'start_time_delta': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time_unit': ('django.db.models.fields.CharField', [], {'default': "u'hours'", 'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'system.program': {
            'Meta': {'object_name': 'Program'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 6, 0, 0)'}),
            'time_factor': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '5', 'decimal_places': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'system.sms': {
            'Meta': {'object_name': 'SMS'},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['system.Page']", 'unique': 'True', 'primary_key': 'True'})
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