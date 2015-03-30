# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework.filters import SearchFilter


class VariableSearchFilter(SearchFilter):

    search_param = "query"
