import json


class DxMixin(object):
    @classmethod
    def get_param_from_request(cls, request, param_name):
        def json_loads(value, default):
            try:
                json_object = json.loads(value)
            except json.JSONDecodeError as e:
                return default
            return json_object

        param_list = []
        if param_name in request.query_params:
            param_list = request.query_params.getlist(param_name)
        elif param_name + "[]" in request.query_params:
            param_list = request.query_params.getlist(param_name + "[]")

        param_list = [json_loads(x, x) for x in param_list]
        if len(param_list) == 1:
            return param_list[0]
        elif len(param_list) > 1:
            return param_list

        return request.data.get(param_name)

    @classmethod
    def get_ordering(cls, dx_sort_list):
        result = []
        if dx_sort_list is None:
            return result
        if isinstance(dx_sort_list, dict):
            dx_sort_list = [dx_sort_list]
        for param in dx_sort_list:
            result.append(("-" if "desc" in param and param["desc"] else '') + param["selector"].replace(".", "__"))
        return result
