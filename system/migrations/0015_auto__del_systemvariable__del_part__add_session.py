# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'SystemVariable'
        db.delete_table(u'system_systemvariable')

        # Deleting model 'Part'
        db.delete_table(u'system_part')

        # Removing M2M table for field vars_used on 'Part'
        db.delete_table(db.shorten_name(u'system_part_vars_used'))

        # Removing M2M table for field content on 'Part'
        db.delete_table(db.shorten_name(u'system_part_content'))

        # Adding model 'Session'
        db.create_table(u'system_session', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('program', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.Program'])),
            ('admin_note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_time_delta', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('start_time_unit', self.gf('django.db.models.fields.CharField')(default=u'hours', max_length=32)),
            ('end_time_delta', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('end_time_unit', self.gf('django.db.models.fields.CharField')(default=u'hours', max_length=32)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('data', self.gf('jsonfield.fields.JSONField')(default=u'undefined')),
        ))
        db.send_create_signal(u'system', ['Session'])

        # Adding M2M table for field content on 'Session'
        m2m_table_name = db.shorten_name(u'system_session_content')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('session', models.ForeignKey(orm[u'system.session'], null=False)),
            ('content', models.ForeignKey(orm[u'system.content'], null=False))
        ))
        db.create_unique(m2m_table_name, ['session_id', 'content_id'])

        # Adding M2M table for field vars_used on 'Session'
        m2m_table_name = db.shorten_name(u'system_session_vars_used')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('session', models.ForeignKey(orm[u'system.session'], null=False)),
            ('variable', models.ForeignKey(orm[u'system.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['session_id', 'variable_id'])


    def backwards(self, orm):
        # Adding model 'SystemVariable'
        db.create_table(u'system_systemvariable', (
            ('value', self.gf('jsonfield.fields.JSONField')(default={})),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
        ))
        db.send_create_signal(u'system', ['SystemVariable'])

        # Adding model 'Part'
        db.create_table(u'system_part', (
            ('start_time_delta', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('admin_note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('data', self.gf('jsonfield.fields.JSONField')(default=u'undefined')),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True, blank=True)),
            ('end_time_unit', self.gf('django.db.models.fields.CharField')(default=u'hours', max_length=32)),
            ('program', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.Program'])),
            ('end_time_delta', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('start_time_unit', self.gf('django.db.models.fields.CharField')(default=u'hours', max_length=32)),
        ))
        db.send_create_signal(u'system', ['Part'])

        # Adding M2M table for field vars_used on 'Part'
        m2m_table_name = db.shorten_name(u'system_part_vars_used')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('part', models.ForeignKey(orm[u'system.part'], null=False)),
            ('variable', models.ForeignKey(orm[u'system.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['part_id', 'variable_id'])

        # Adding M2M table for field content on 'Part'
        m2m_table_name = db.shorten_name(u'system_part_content')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('part', models.ForeignKey(orm[u'system.part'], null=False)),
            ('content', models.ForeignKey(orm[u'system.content'], null=False))
        ))
        db.create_unique(m2m_table_name, ['part_id', 'content_id'])

        # Deleting model 'Session'
        db.delete_table(u'system_session')

        # Removing M2M table for field content on 'Session'
        db.delete_table(db.shorten_name(u'system_session_content'))

        # Removing M2M table for field vars_used on 'Session'
        db.delete_table(db.shorten_name(u'system_session_vars_used'))


    models = {
        u'system.content': {
            'Meta': {'object_name': 'Content'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'[]'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'system.program': {
            'Meta': {'object_name': 'Program'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 9, 0, 0)'}),
            'time_factor': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '5', 'decimal_places': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'system.session': {
            'Meta': {'object_name': 'Session'},
            'admin_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['system.Content']", 'null': 'True', 'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            'end_time_delta': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end_time_unit': ('django.db.models.fields.CharField', [], {'default': "u'hours'", 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['system.Program']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'start_time_delta': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time_unit': ('django.db.models.fields.CharField', [], {'default': "u'hours'", 'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'vars_used': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['system.Variable']", 'symmetrical': 'False'})
        },
        u'system.variable': {
            'Meta': {'object_name': 'Variable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'var_type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['system']