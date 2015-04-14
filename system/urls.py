from __future__ import unicode_literals

from django.conf.urls import patterns, url, include
from rest_framework import routers

from system.views import VariableViewSet, VariableSearchViewSet, ExpressionViewSet


router = routers.DefaultRouter()
router.register(r'variables/search', VariableSearchViewSet)
router.register(r'evaluate-expression', ExpressionViewSet, base_name="evaluate-expression-viewset")
router.register(r'variables', VariableViewSet)

urlpatterns = patterns(
    '',
    url(r'', include(router.urls)),
)

