# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SMS.title'
        db.add_column(u'content_sms', 'title',
                      self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=64, blank=True),
                      keep_default=False)

        # Adding field 'SMS.part'
        db.add_column(u'content_sms', 'part',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.Part'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'SMS.admin_note'
        db.add_column(u'content_sms', 'admin_note',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding M2M table for field vars_used on 'SMS'
        m2m_table_name = db.shorten_name(u'content_sms_vars_used')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sms', models.ForeignKey(orm[u'content.sms'], null=False)),
            ('variable', models.ForeignKey(orm[u'system.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sms_id', 'variable_id'])

        # Adding field 'Email.title'
        db.add_column(u'content_email', 'title',
                      self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=64, blank=True),
                      keep_default=False)

        # Adding field 'Email.part'
        db.add_column(u'content_email', 'part',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.Part'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Email.admin_note'
        db.add_column(u'content_email', 'admin_note',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding M2M table for field vars_used on 'Email'
        m2m_table_name = db.shorten_name(u'content_email_vars_used')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('email', models.ForeignKey(orm[u'content.email'], null=False)),
            ('variable', models.ForeignKey(orm[u'system.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['email_id', 'variable_id'])


    def backwards(self, orm):
        # Deleting field 'SMS.title'
        db.delete_column(u'content_sms', 'title')

        # Deleting field 'SMS.part'
        db.delete_column(u'content_sms', 'part_id')

        # Deleting field 'SMS.admin_note'
        db.delete_column(u'content_sms', 'admin_note')

        # Removing M2M table for field vars_used on 'SMS'
        db.delete_table(db.shorten_name(u'content_sms_vars_used'))

        # Deleting field 'Email.title'
        db.delete_column(u'content_email', 'title')

        # Deleting field 'Email.part'
        db.delete_column(u'content_email', 'part_id')

        # Deleting field 'Email.admin_note'
        db.delete_column(u'content_email', 'admin_note')

        # Removing M2M table for field vars_used on 'Email'
        db.delete_table(db.shorten_name(u'content_email_vars_used'))


    models = {
        u'content.email': {
            'Meta': {'object_name': 'Email'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Part']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'content.sms': {
            'Meta': {'object_name': 'SMS'},
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

    complete_apps = ['content']