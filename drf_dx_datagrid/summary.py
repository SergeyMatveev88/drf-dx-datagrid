# coding: utf-8
from django.db.models import *
from rest_framework.exceptions import ValidationError


def _get_aggregate_function(function_name, field_name):
    if function_name == "count":
        return Count(field_name)
    elif function_name == "avg":
        return Avg(field_name)
    elif function_name == "max":
        return Max(field_name)
    elif function_name == "min":
        return Min(field_name)
    elif function_name == "sum":
        return Sum(field_name)
    else:
        raise ValidationError(detail="Unsupported summary type '%s'" % function_name)


class SummaryMixin(object):

    def get_aggregate_function(self, function_name, field_name):
        return _get_aggregate_function(function_name, field_name)

    def calc_total_summary(self, queryset, summary_list):
        result = []
        for summary in summary_list:
            field_name = summary["selector"].replace(".", "__")
            aggr_function = self.get_aggregate_function(summary["summaryType"], field_name)
            if aggr_function is None:
                result.append(None)
            else:
                summary_qset = queryset.aggregate(aggr_function)
                result.append(list(summary_qset.values())[0])
        return result

    def add_summary_annotate(self, queryset, summary_list):
        summary_param_dict = {}
        for summary in summary_list:
            field_name = summary["selector"].replace(".", "__")
            aggr_function = self.get_aggregate_function(summary["summaryType"], field_name)
            param_name = "gs__"+str(summary_list.index(summary))
            summary_param_dict[param_name] = aggr_function
        return queryset.annotate(**summary_param_dict)
