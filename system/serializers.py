from __future__ import unicode_literals

from rest_framework import serializers

from system.models import Variable
from system.expressions import Parser, ParseException


class VariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variable
        read_only_fields = ['id']


class ExpressionSerializer(serializers.Serializer):

    query = serializers.CharField()
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if "query" in obj:
            p = Parser(user_obj=self.context["request"].user)
            return p.parse(obj["query"])

    def create(self, validated_data):
        return {"query": validated_data.pop("query")}