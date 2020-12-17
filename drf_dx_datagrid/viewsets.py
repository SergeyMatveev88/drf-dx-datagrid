from collections import OrderedDict

import rest_framework.viewsets
from django.db.models import Count
from rest_framework.response import Response

from .filters import DxFilterBackend
from .mixins import DxMixin
from .pagination import TakeSkipPagination
from .summary import SummaryMixin


class DxModelViewSet(rest_framework.viewsets.ModelViewSet, DxMixin, SummaryMixin):
    pagination_class = TakeSkipPagination
    filter_backends = [DxFilterBackend, *rest_framework.viewsets.ModelViewSet.filter_backends]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        group = self.get_param_from_request(request, "group")
        if group is None:
            return self._not_grouped_list(queryset, request)
        else:
            return self._grouped_list(group, queryset, request)

    def _grouped_list(self, group, queryset, request):
        def _format_row_data(row, group_field_name):
            result = {"key": row[group_field_name], "items": None, "summary": [100], "count": row["count"]}
            summary_pairs = list(filter(lambda x: x[0].startswith("gs__"), row.items()))
            if summary_pairs:
                summary_pairs.sort(key=lambda x: x[0])
                summary = [x[1] for x in summary_pairs]
                result["summary"] = summary
            return result

        require_group_count = self.get_param_from_request(request, "requireGroupCount")
        require_total_count = self.get_param_from_request(request, "requireTotalCount")
        if group[0]["isExpanded"]:
            return Response()
        else:
            group_field_name = group[0]["selector"].replace(".", "__")
            ordering = self.get_ordering(group)
            group_queryset = queryset.values(group_field_name).annotate(count=Count("pk")).order_by(
                *ordering).distinct()
            group_summary = self.get_param_from_request(request, "groupSummary")
            if group_summary is not None and group_summary:
                group_summary_list = group_summary if isinstance(group_summary, list) else [group_summary]
                group_queryset = self.add_summary_annotate(group_queryset, group_summary_list)
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
                res_dict["data"] = [_format_row_data(x, group_field_name) for x in page]
                return Response(res_dict)
            else:
                res_dict["data"] = [_format_row_data(x, group_field_name) for x in group_queryset]
            return Response(res_dict)

    def _not_grouped_list(self, queryset, request):
        res_dict = OrderedDict()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            res_dict["totalCount"] = self.paginator.count
        else:
            serializer = self.get_serializer(queryset, many=True)
        total_summary = self.get_param_from_request(request, "totalSummary")
        if total_summary is not None and total_summary:
            total_summary_list = total_summary if isinstance(total_summary, list) else [total_summary]
            res_dict["summary"] = self.calc_total_summary(queryset, total_summary_list)
        res_dict["data"] = serializer.data
        return Response(res_dict)
