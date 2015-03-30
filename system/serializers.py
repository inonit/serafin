from __future__ import unicode_literals

from rest_framework import serializers

from system.models import Variable


class VariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variable
        read_only_fields = ['id']
