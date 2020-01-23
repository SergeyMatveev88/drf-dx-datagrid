from rest_framework.pagination import LimitOffsetPagination, _positive_int
from rest_framework.response import Response
from collections import OrderedDict


class TakeSkipPagination(LimitOffsetPagination):
    limit_query_param = 'take'
    offset_query_param = 'skip'

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param] if self.limit_query_param in request.query_params
                    else request.data[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit

    def get_offset(self, request):
        try:
            return _positive_int(
                request.query_params[self.offset_query_param] if self.offset_query_param in request.query_params
                else request.data[self.offset_query_param],
            )
        except (KeyError, ValueError):
            return 0

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        if self.limit is None and self.offset is None:
            return None
        self.request = request

        if self.limit is not None and self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []

        if self.limit is None:
            return list(queryset[self.offset:])
        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('totalCount', self.count),
            ('data', data)
        ]))
