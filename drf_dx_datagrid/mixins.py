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

        if param_name + "[]" in request.query_params:
            raw_list = request.query_params.getlist(param_name + "[]")
            return [json_loads(x, x) for x in raw_list]
        if param_name in request.query_params:
            param_value = request.query_params.get(param_name)
            if param_value != '':
                return json.loads(param_value)
        return request.data.get(param_name)

    @classmethod
    def get_ordering(cls, dx_sort_list):
        if dx_sort_list is None:
            return []
        result = []
        for param in dx_sort_list:
            result.append(("-" if "desc" in param and param["desc"] else '') + param["selector"].replace(".", "__"))
        return result
