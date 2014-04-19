# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Variable'
        db.create_table(u'system_variable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('var_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'system', ['Variable'])

        # Adding M2M table for field vars_used on 'Page'
        m2m_table_name = db.shorten_name(u'system_page_vars_used')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm[u'system.page'], null=False)),
            ('variable', models.ForeignKey(orm[u'system.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['page_id', 'variable_id'])

        # Adding unique constraint on 'Page', fields ['title']
        db.create_unique(u'system_page', ['title'])

        # Adding M2M table for field vars_used on 'Part'
        m2m_table_name = db.shorten_name(u'system_part_vars_used')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('part', models.ForeignKey(orm[u'system.part'], null=False)),
            ('variable', models.ForeignKey(orm[u'system.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['part_id', 'variable_id'])

        # Adding unique constraint on 'Part', fields ['title']
        db.create_unique(u'system_part', ['title'])

        # Adding unique constraint on 'Program', fields ['title']
        db.create_unique(u'system_program', ['title'])


    def backwards(self, orm):
        # Removing unique constraint on 'Program', fields ['title']
        db.delete_unique(u'system_program', ['title'])

        # Removing unique constraint on 'Part', fields ['title']
        db.delete_unique(u'system_part', ['title'])

        # Removing unique constraint on 'Page', fields ['title']
        db.delete_unique(u'system_page', ['title'])

        # Deleting model 'Variable'
        db.delete_table(u'system_variable')

        # Removing M2M table for field vars_used on 'Page'
        db.delete_table(db.shorten_name(u'system_page_vars_used'))

        # Removing M2M table for field vars_used on 'Part'
        db.delete_table(db.shorten_name(u'system_part_vars_used'))


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
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Program']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'system.program': {
            'Meta': {'object_name': 'Program'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'system.variable': {
            'Meta': {'object_name': 'Variable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'var_type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['system']