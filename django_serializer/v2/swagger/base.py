from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from django import urls
from django.conf import settings
from django.forms import forms

from django_serializer.v2.swagger import utils
from django_serializer.v2.exceptions import HttpError, HttpFormError
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
        if issubclass(type(schema), HttpError):
            description = schema.description
            schema = utils.generate_error_schema(self, schema)
        if schema is None:
            return {'description': description}
        return {'description': description,
                'content': {'application/json': {'schema': schema}}}

    def _generate_request_body(self, schema):
        return {'content': {'application/json': {
            'schema': self.ma_spec.converter.schema2jsonschema(schema)
        }}}

    def _resolve_forms(self, meta):
        query_schema = utils.merge_schemas(
            utils.form2schema(getattr(meta, 'query_form', None)),
            utils.form2schema(getattr(getattr(meta, 'paginator', None),
                                      'form', None)))
        body_schema = utils.merge_schemas(
            utils.form2schema(getattr(meta, 'body_form', None)),
            utils.form2schema(getattr(meta, 'model_form', None)))

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
        parameters = self._resolve_forms(meta)
        if len(parameters) != 0:
            meta.errors.append(HttpFormError)

        responses = {200: self._generate_response(meta.serializer)}
        for err in meta.errors:
            if err == HttpFormError:
                err = err(forms.Form())
            else:
                err = err()
            responses.update({err.http_code: self._generate_response(err)})

        for tag in meta.tags:
            self.tags.add(tag)

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
        for url, view in self.urls_views.items():
            self._spec.path(
                url,
                schema=view.Meta.serializer,
                summary=view.Meta.summary,
                description=view.Meta.description,
                view=view,
                operations=self._generate_operations(view.Meta),
            )

    def _generate_tags(self):
        for tag in self.tags:
            self._spec.tag({'name': tag, 'description': tag})

    def generate(self):
        self._get_views()
        self._generate_paths()
        self._generate_tags()
