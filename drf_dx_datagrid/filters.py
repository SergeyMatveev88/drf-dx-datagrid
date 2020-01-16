from rest_framework import filters
from django.db.models import Q
from .mixins import DxMixin


class DxFilterBackend(filters.BaseFilterBackend, DxMixin):

    def __is_leaf(self, dx_filter):
        for elem in dx_filter:
            if isinstance(elem, list):
                return False
        return True

    def __to_django_operator(self, operator):
        if operator == "=":
            return ""
        elif operator == ">":
            return "__gt"
        elif operator == "<":
            return "__lt"
        elif operator == ">=":
            return "__gte"
        elif operator == "<=":
            return "__lte"
        else:
            return "__" + operator

    def __leaf_node_to_q(self, leaf):
        field_name = leaf[0].replace(".", "__")
        if len(leaf) == 2 and leaf[1] == "=":
            kwargs = {}
            kwargs[field_name + "__isnull"] = True
            return Q(**kwargs)
        elif leaf[1] == "<>":
            kwargs = {}
            kwargs[field_name] = leaf[2]
            return ~Q(**kwargs)
        elif leaf[1] == "notcontains":
            kwargs = {}
            kwargs[field_name + "__contains"] = leaf[2]
            return ~Q(**kwargs)
        else:
            kwargs = {}
            kwargs[field_name + self.__to_django_operator(leaf[1])] = leaf[2]
            return Q(**kwargs)

    def __generate_q_expr(self, dx_filter):
        if dx_filter is None or not dx_filter:
            return None
        if self.__is_leaf(dx_filter):
            return self.__leaf_node_to_q(dx_filter)
        else:
            q_elems = []

            for elem in dx_filter:
                if isinstance(elem, list):
                    q_elems.append(self.__generate_q_expr(elem))
                elif elem in ["and", "or"]:
                    q_elems.append(elem)
                else:
                    raise Exception("Невозможно применить данный поиск")
            q_expr = q_elems[0]
            for num_pair in range(0, len(q_elems) // 2):
                oper = q_elems[num_pair * 2 + 1]
                if oper == "and":
                    q_expr = q_expr & q_elems[(num_pair + 1) * 2]
                else:
                    q_expr = q_expr | q_elems[(num_pair + 1) * 2]
            return q_expr

    def filter_queryset(self, request, queryset, view):
        res_queryset = queryset
        filter = self.get_param_from_request(request, "filter")
        if filter:
            q_expr = self.__generate_q_expr(filter)
            if q_expr is not None:
                res_queryset = res_queryset.filter(q_expr)
        sort = self.get_param_from_request(request, "sort")
        if sort:
            ordering = self.get_ordering(sort)
            if ordering:
                res_queryset = res_queryset.order_by(*ordering)
        return res_queryset
