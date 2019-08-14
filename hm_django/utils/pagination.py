#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PlugPageNumberPagination(PageNumberPagination):
    page_query_param = 'p'  # 请求第几页
    page_size_query_param = 'size'  # 每页多少条数据

    def get_paginated_response(self, data):
        return Response(dict([
            ('count', self.page.paginator.count),
            ('current_page', self.page.number),
            ('per_page', self.page.paginator.per_page),
            ('total_page', self.page.paginator.num_pages),
            ('results', data)
        ]))
