from collections import OrderedDict

import rest_framework.viewsets
from django.db.models import Count
from rest_framework.response import Response

from .filters import DxFilterBackend
from .mixins import DxMixin
from .pagination import TakeSkipPagination
from .summary import SummaryMixin


def format_items(lvl_dict, lvl_items):
    if lvl_dict is None:
        return
    for key in lvl_dict:
        key_dict = lvl_dict[key]
        item = {"key": key}
        lvl_items.append(item)

        if "count" in key_dict:
            item["count"] = key_dict["count"]
        if "summary" in key_dict:
            item["summary"] = key_dict["summary"]

        if key_dict["items"] is None:
            item["items"] = None
        else:
            item["items"] = []
            format_items(key_dict["items"], item["items"])


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

    def _grouped_list(self, groups, queryset, request):
        require_group_count = self.get_param_from_request(request, "requireGroupCount")
        require_total_count = self.get_param_from_request(request, "requireTotalCount")

        if not isinstance(groups, list):
            groups = [groups]

        group_field_names = {self.get_group_field_name(group) for group in groups}
        ordering = self.get_ordering(groups)
        group_queryset = queryset.values(*group_field_names).annotate(count=Count("pk")).order_by(*ordering).distinct()
        group_summary = self.get_param_from_request(request, "groupSummary")
        if group_summary is not None and group_summary:
            group_summary_list = group_summary if isinstance(group_summary, list) else [group_summary]
            group_queryset = self.add_summary_annotate(group_queryset, group_summary_list)

        page = self.paginate_queryset(group_queryset)
        res_dict = {}
        if require_group_count:
            res_dict["groupCount"] = group_queryset.count()
        if require_total_count:
            res_dict["totalCount"] = queryset.count()

        rs = page if page is not None else group_queryset
        data_dict = {}
        for row in rs:
            lvl_dict = data_dict
            for group in groups:
                group_field_name = self.get_group_field_name(group)
                key = row[group_field_name]

                if key in lvl_dict:
                    key_dict = lvl_dict[key]
                else:
                    key_dict = {}
                    lvl_dict[key] = key_dict

                if group["isExpanded"]:
                    if "items" not in key_dict:
                        key_dict["items"] = {}
                    lvl_dict = key_dict["items"]
                else:
                    key_dict["items"] = None
                    key_dict["count"] = row["count"]

                    summary_pairs = list(filter(lambda x: x[0].startswith("gs__"), row.items()))
                    if summary_pairs:
                        summary_pairs.sort(key=lambda x: x[0])
                        summary = [x[1] for x in summary_pairs]
                        key_dict["summary"] = summary

        res_dict["data"] = []
        format_items(data_dict, res_dict["data"])

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

    def get_group_field_name(self, group):
        if "groupInterval" in group:
            return group["selector"].replace(".", "__") + "__" + group["groupInterval"]
        else:
            return group["selector"].replace(".", "__")
