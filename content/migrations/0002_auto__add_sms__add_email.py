# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SMS'
        db.create_table(u'content_sms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default=u'undefined')),
        ))
        db.send_create_signal(u'content', ['SMS'])

        # Adding model 'Email'
        db.create_table(u'content_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default=u'undefined')),
        ))
        db.send_create_signal(u'content', ['Email'])


    def backwards(self, orm):
        # Deleting model 'SMS'
        db.delete_table(u'content_sms')

        # Deleting model 'Email'
        db.delete_table(u'content_email')


    models = {
        u'content.email': {
            'Meta': {'object_name': 'Email'},
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'content.sms': {
            'Meta': {'object_name': 'SMS'},
            'data': ('jsonfield.fields.JSONField', [], {'default': "u'undefined'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['content']