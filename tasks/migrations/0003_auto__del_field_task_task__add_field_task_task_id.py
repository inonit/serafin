# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Task.task'
        db.delete_column(u'tasks_task', 'task')

        # Adding field 'Task.task_id'
        db.add_column(u'tasks_task', 'task_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Task.task'
        raise RuntimeError("Cannot reverse this migration. 'Task.task' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Task.task'
        db.add_column(u'tasks_task', 'task',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)

        # Deleting field 'Task.task_id'
        db.delete_column(u'tasks_task', 'task_id')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['tasks']