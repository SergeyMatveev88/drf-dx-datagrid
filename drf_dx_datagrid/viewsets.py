from .mixins import DxMixin
import rest_framework.viewsets
from django.db.models import Count
from rest_framework.response import Response
from .pagination import TakeSkipPagination
from .filters import DxFilterBackend


class DxModelViewSet(rest_framework.viewsets.ModelViewSet, DxMixin):
    pagination_class = TakeSkipPagination
    filter_backends = [DxFilterBackend, *rest_framework.viewsets.ModelViewSet.filter_backends]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        group = self.get_param_from_request(request, "group")
        if group is None:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response({"data": serializer.data})
        else:
            require_group_count = self.get_param_from_request(request, "requireGroupCount")
            require_total_count = self.get_param_from_request(request, "requireTotalCount")
            if group[0]["isExpanded"]:
                return Response()
            else:
                group_field_name = group[0]["selector"].replace(".", "__")
                ordering = self.get_ordering(group)
                group_queryset = queryset.values(group_field_name).annotate(count=Count("pk")).order_by(
                    *ordering).distinct()
                page = self.paginate_queryset(group_queryset)
                res_dict = {}
                if require_total_count is None and require_group_count is None:
                    res_dict["totalCount"] = group_queryset.count()
                else:
                    if require_group_count:
                        res_dict["groupCount"] = group_queryset.count()
                    if require_total_count:
                        res_dict["totalCount"] = queryset.count()
                if page is not None:
                    res_dict["data"] = [{"key": x[group_field_name], "items": None, "count": x["count"]} for x in page]
                    return Response(res_dict)
                else:
                    res_dict["data"] = [{"key": x[group_field_name], "items": None, "count": x["count"]} for x in
                                        group_queryset]
                return Response(res_dict)
