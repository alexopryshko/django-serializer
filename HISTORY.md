# 1.1.0 - not released
    - fix view discovery in swagger generation
    - add new `django_serializer.v2.views.paginator.BasePaginator`
    - add new `django_serializer.v2.views.paginator.LimitOffsetPaginator`
    - add new `django_serializer.v2.views.generics.ListApiView.get_paginator_class`
    - add new `django_serializer.v2.views.generics.ListApiView.get_paginator`
    - add new `django_serializer.v2.views.base.ApiView.get_serializer_class`
    - add new `django_serializer.v2.views.base.ApiView.get_serializer`
    - `django_serializer.v2.views.paginator.Paginator` marked as deprecated, use `django_serializer.v2.views.paginator.BasePaginator` instead
    - `django_serializer.v2.views.paginator.BasePaginator` `qs` argument will become mandatory in the future
    - `django_serializer.v2.views.base.ApiView.get_serializer_kwargs` now adds `request` and `many` to serializer kwargs 
    - `django_serializer.v2.views.base.ApiView._serializer_pipeline` no longer passes `many` parameter to `Serializer.dump`
    - `django_serializer.v2.views.base.ApiView._serializer_pipeline` is instance method instead of static method
    - `django_serializer.v2.views.base.ApiView._generic_response` is instance method instead of static method
    - `django_serializer.v2.views.base.ApiView._json_response` is instance method instead of static method
---
# 1.0.0
