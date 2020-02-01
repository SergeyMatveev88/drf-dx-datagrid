# drf-dx-datagrid
# Overview
This package provides easy integration between [Django REST framework](https://www.django-rest-framework.org) and [DevExreme Data Grid](https://js.devexpress.com/Demos/WidgetsGallery/Demo/DataGrid/Overview/jQuery/Light/)

Install drf-dx-datagrid, replace classname ModelViewSet to DxModelViewSet in your django project and it will return a JSON structure that is fully compatible with what Data Grid expects.
It handles grouping, paging, filtering and ordering on serverside.

# Configuration
Define your ModelViewSet classes as on this example:
```python
from drf_dx_datagrid import DxModelViewSet

class MyModelViewSet(DxModelViewSet):
    serializer_class = MyModelSerializer
    queryset = core.models.MyModel.objects.all()
```
JS example:
```js
import CustomStore from 'devextreme/data/custom_store';
import axios from "axios";

export const getUpsStore = (my_url, customStoreOptions) => {
    const load = (loadOptions) => {
        return axios(`${my_url}`, {
                params: loadOptions
            }
        ).then((response) => response.data
        )
    };
    return new CustomStore({...customStoreOptions, load: load});
}
```    
