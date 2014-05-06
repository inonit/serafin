from __future__ import unicode_literals

from import_export import resources, fields, widgets
from users.models import User
import functools


class SmartManyToManyWidget(widgets.ManyToManyWidget):
    '''Replacement ManyToManyWidget that allows import of m2m relations by name'''

    def clean(self, value):
        if not value:
            return self.model.objects.none()
        values = [v.strip() for v in value.split(",")]
        try:
            discard = int(values[0])
            # ok, we have ints
            queryset = self.model.objects.filter(pk__in=values)
            if len(queryset) != len(values):
                for value in values:
                    obj, created = self.model.objects.get_or_create(pk=value)
                queryset = self.model.objects.filter(pk__in=values)
            return queryset
        except:
            # ok, we (probably) have names
            queryset = self.model.objects.filter(name__in=values)
            if len(queryset) != len(values):
                for value in values:
                    obj, created = self.model.objects.get_or_create(name=value)
                queryset = self.model.objects.filter(name__in=values)
            return queryset

    def render(self, value):
        values = [obj.__unicode__() for obj in value.all()]
        return ', '.join(values)


class UserResource(resources.ModelResource):
    '''Import-Export resource for User model'''

    data = fields.Field(column_name='...')
    email = fields.Field()
    phone = fields.Field()
    data_headers = []

    @classmethod
    def widget_from_django_field(cls, f, default=widgets.Widget):
        result = super(cls, cls).widget_from_django_field(f, default)
        internal_type = f.get_internal_type()
        if internal_type in ('ManyToManyField', ):
            result = functools.partial(SmartManyToManyWidget, model=f.rel.to)
        return result

    def import_obj(self, obj, data, dry_run):
        fields = [field for field in self.get_fields() if field.column_name != '...']

        for field in fields:
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            self.import_field(field, obj, data)

        headers = [field.column_name for field in self.get_fields()
            if field.column_name not in ['...', 'email', 'phone']]

        if not obj.data:
            obj.data = {}

        for key in data.keys():
            if key in headers:
                continue
            obj.data[key] = data[key]

    def export_resource(self, obj):
        fields = [self.export_field(field, obj) for field in self.get_fields()
            if field.column_name not in ['...', 'email', 'phone']]

        for field in self.data_headers:
            if field in obj.data:
                fields.append(obj.data.get(field))
            else:
                fields.append('')

        return fields

    def get_export_headers(self):
        headers = [field.column_name for field in self.get_fields()
            if field.column_name not in ['...', 'email', 'phone']]
        queryset = self.get_queryset()

        data_headers = set()
        for obj in queryset:
            data_headers.update(obj.data.keys())

        self.data_headers = list(data_headers)
        headers += self.data_headers

        return headers

    class Meta:
        model = User
        export_order = [
            'id',
            'groups',
            'email',
            'phone',
            'data'
        ]
        exclude = [
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
