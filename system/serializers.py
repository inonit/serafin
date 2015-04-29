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
    response = serializers.SerializerMethodField()

    @staticmethod
    def get_response(obj):
        return obj["response"]

    def validate(self, data):
        p = Parser(user_obj=self.context["request"].user)
        response = {
            "result": None,
            "reason": None
        }
        try:
            response["result"] = p.parse(data["query"])
        except (ParseException, ZeroDivisionError, KeyError) as e:
            response["result"] = None
            response["reason"] = unicode(e)
        except Exception:
            response["result"] = None
            response["reason"] = _("")

        data["response"] = response
        return data

    def create(self, validated_data):
        return validated_data