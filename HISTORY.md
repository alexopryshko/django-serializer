# 1.2.1
- fix SERIALIZER_FIELD_MAPPING

# 1.2.0
- drop support for django2
- add django4.2 to test matrix

- `django_serializer.base_views.BaseView` deprecated. It will be removed in version 2.0
- `django_serializer.serializer.base.Serializer` deprecated. It will be removed in version 2.0


- add `django_serializer.v2.renderers.BaseRenderer` see docstrings
- add `django_serializer.v2.renderers.JsonRenderer` see docstrings
- add `SERIALIZER_DEFAULT_PARSER_CLASS` to django settings
- add `ApiViewMeta.body_parser`


- add `django_serializer.v2.parsers.BaseParser` see docstrings
- add `django_serializer.v2.parsers.JsonParser` see docstrings
- add `django_serializer.v2.exceptions.parser.ParseException`
- add `SERIALIZER_DEFAULT_RENDERER_CLASS` to django settings
- add `ApiViewMeta.renderer`


- add `ApiView.get_parser` method
- `ApiView.get_request_json` now uses `ApiView.get_parser` for parsing request.body


- `ApiView._query_form` now has positional request argument
- `ApiView.__body_form` now has positional request argument
- `ApiView.perform_response_pipelines` now has positional request argument
- added new `ApiView._check_request_method` method
- added new `ApiView._check_section_permission` method
- `django_serializer.v2.views.mixins.LoginRequiredMixin` now uses `ApiView._check_section_permission` 
- add `_check_request_method` and `_check_section_permission` to `ApiView.perform_request_pipelines`
- `ApiView._json_response` renamed to `ApiView.render_response`. `ApiView.render_response` uses renderer logic


- `ApiView._handle_http_error` renamed to `ApiView.handle_http_error`
- `ApiView.handle_http_error` now has positional request argument
- `ApiView.handle_http_error` uses `ApiView.render_response`


- `SERIALIZER_FIELD_MAPPING` no longer importable from `django_serializer/v2/serializer/__init__.py`
- `FileField` moved from `django_serializer/v2/serializer/__init__.py` to `django_serializer/v2/serializer_fields.py`


## internal changes
- add `django_serializer.v2.settings.ApiSettings` 
- add multiple docstrings
- reformated code with black
- fix typings
- drop django2 from test matrix

# 1.1.0
- minimum supported django>=2.2
- minimum supported marshmallow>=3.14.0
- minimum supported apispec>=5.1.1
- added python 3.7, 3.8, 3.9, 3.10 to test matrix
- added django 2.2, 3.2, 4.0, 4.1 to test matrix

- fix view discovery in swagger generation
- add `django.db.models.BigAutoField` to serializer field mapping
- add `django.db.models.SlugField` to serializer field mapping
- add `django.db.models.DurationField` to serializer field mapping
- add `django.db.models.FileField` to serializer field mapping
- add `django.db.models.ImageField` to serializer field mapping
- add `django.db.models.UUIDField` to serializer field mapping
- add `django.db.models.GenericIPAddressField` to serializer field mapping
- add new `django_serializer.v2.serializer.fields.FileField` to serialize file fields
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
- `django_serializer.v2.serializer.fields` no longer importable, use `marshmallow.fields` instead

## internal changes
- bump pytest==6.2.5
- add to test requirements pytz==2022.6
---
# 1.0.0
