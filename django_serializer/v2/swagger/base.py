from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from django import urls
from django.conf import settings

from django_serializer.swagger.utils import form2schema, _merge_schemas
from django_serializer.v2.exceptions import HttpError
from django_serializer.v2.views import ApiView


class Swagger:
    def __init__(self):
        self.project_name = getattr(settings, 'SWAGGER_PROJECT_NAME', 'default')
        self.version = getattr(settings, 'SWAGGER_PROJECT_VERSION', '1.0.0')
        self.openapi = getattr(settings, 'SWAGGER_OPENAPI_VERSION', '3.0.2')
        self._spec = APISpec(
            title=self.project_name,
            version=self.version,
            openapi_version=self.openapi,
            plugins=[MarshmallowPlugin()],
        )
        self.urls_views = {}
        self.tags = set()
        self.error_classes = {}
        self.ma_spec = MarshmallowPlugin()
        self.ma_spec.init_spec(self._spec)

    @property
    def spec(self):
        return self._spec.to_dict()

    def _get_views(self):
        views = urls.get_resolver(None).reverse_dict.items()
        for view, url in views:
            try:
                class_ = view.view_class
                if issubclass(class_, ApiView):
                    url = '/' + url[0][0][0].lstrip('/')
                    self.urls_views[url] = class_
            except AttributeError:
                continue

    def _generate_response(self, schema, description='success'):
        from django_serializer.swagger.utils import _generate_error_schema
        if issubclass(type(schema), HttpError):
            description = schema.description
            schema = _generate_error_schema(self, schema)
        schema_name = self.ma_spec.schema_name_resolver(schema)
        return {'description': description,
                'content': {'application/json': {'schema': schema_name}}}

    def _generate_request_body(self, schema):
        return {"content": {"application/json": {
            "schema": self.ma_spec.converter.schema2jsonschema(schema)
        }}}

    def _resolve_forms(self, meta):
        query_schema = form2schema(getattr(meta, 'query_form', None))
        body_schema = _merge_schemas(
            form2schema(getattr(meta, 'body_form', None)),
            form2schema(getattr(meta, 'model_form', None)))

        parameters = {}
        if query_schema is not None:
            parameters.update({'query': self.ma_spec.converter
                              .schema2parameters(query_schema,
                                                 default_in='query')})
        if body_schema is not None:
            parameters.update(
                {'requestBody': self._generate_request_body(body_schema)})
        return parameters

    def _generate_operations(self, meta):
        responses = {200: self._generate_response(meta.serializer)}
        for err in meta.errors:
            err = err()
            responses.update({err.http_code: self._generate_response(err)})

        [self.tags.add(tag) for tag in meta.tags]

        parameters = self._resolve_forms(meta)

        operation = {
            'responses': responses,
            'tags': meta.tags
        }

        if parameters.get('query', False):
            operation.update({'parameters': parameters['query']})

        if parameters.get('requestBody', False):
            operation.update({'requestBody': parameters['requestBody']})

        return {meta.method.value: operation}

    def _generate_paths(self):
        for item in self.urls_views.items():
            url, view, meta = item[0], item[1], item[1].Meta
            self._spec.path(
                url,
                schema=meta.serializer,
                summary=meta.summary,
                description=meta.description,
                view=view,
                operations=self._generate_operations(meta),
            )

    def _generate_tags(self):
        [self._spec.tag({"name": tag, "description": tag}) for tag in self.tags]

    def generate(self):
        self._get_views()
        self._generate_paths()
        self._generate_tags()
