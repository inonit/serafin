from __future__ import unicode_literals

from builtins import object
from import_export import resources, fields, widgets
from constance import config
from users.models import User

import functools


class UserResource(resources.ModelResource):
    '''Import-Export resource for User model'''

    data = fields.Field(column_name='...')
    data_headers = []

    def import_obj(self, obj, data, dry_run):
        fields = [field for field in self.get_fields() if field.column_name != '...']

        for field in fields:
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            self.import_field(field, obj, data)

        headers = [field.column_name for field in self.get_fields()
            if field.column_name not in ['...']]

        if not obj.data:
            obj.data = {}

        for key in list(data.keys()):
            if key in headers:
                continue
            obj.data[key] = data[key]

    def export_resource(self, obj):
        fields = [self.export_field(field, obj) for field in self.get_fields() if field.column_name not in ['...']]

        for field in self.data_headers:
            if field in obj.data:
                fields.append(obj.data.get(field))
            else:
                fields.append('')

        return fields

    def get_export_headers(self):
        headers = [field.column_name for field in self.get_fields() if field.column_name not in ['...']]
        queryset = self.get_queryset()

        if config.USER_VARIABLE_EXPORT:
            self.data_headers = [
                field.strip() for field in config.USER_VARIABLE_EXPORT.split(',')
                if field
            ]
            headers += self.data_headers
            return headers

        data_headers = set()
        for obj in queryset:
            data_headers.update(list(obj.data.keys()))

        self.data_headers = list(data_headers)
        headers += self.data_headers

        return headers

    class Meta(object):
        model = User
        export_order = [
            'id',
            'groups',
            'data'
        ]
        exclude = [
            'email',
            'phone',
            'secondary_phone',
            'password',
            'last_login',
            'is_superuser',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined',
            'token',
            'data',
        ]
