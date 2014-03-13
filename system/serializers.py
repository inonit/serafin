from django.contrib.auth.models import Part, Page
from rest_framework import serializers


class PartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Part
        fields = ('part', 'program', 'start_time', 'end_time')


class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('title', )
