from __future__ import unicode_literals

from builtins import str
from builtins import object
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from system.models import Variable
from system.expressions import Parser, ParseException


class VariableSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Variable
        fields = '__all__'
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
            response["reason"] = str(e)
        except Exception:
            response["result"] = None
            response["reason"] = _("An error has occurred. Your expression cannot be "
                                   "evaluated.")

        data["response"] = response
        return data

    def create(self, validated_data):
        return validated_data
