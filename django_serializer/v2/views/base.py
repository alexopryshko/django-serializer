import json
import logging
from json import JSONDecodeError
from typing import Mapping, Type

from django.conf import settings
from django.forms import Form
from django.http import JsonResponse
from django.views import View

from django_serializer.v2.exceptions import (
    HttpNotImplementedError,
    HttpError,
    HttpFormError,
    BadRequestError,
    InternalServerError,
)
from django_serializer.v2.views.meta import ApiViewMeta


class ApiView(View, metaclass=ApiViewMeta, checkmeta=False):
    Meta = ApiViewMeta.Meta

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(
            f'django_serializer.views.{self.__class__.__name__}'
        )

    @property
    def logger(self):
        return self._logger

    @property
    def request_query(self) -> Mapping:
        return getattr(self, '_request_query', None)

    @property
    def request_body(self) -> Mapping:
        return getattr(self, '_request_body', None)

    def get_request_json(self):
        if hasattr(self, '_request_json'):
            return getattr(self, '_request_json')
        if 'application/json' in self.request.content_type:
            try:
                payload = json.loads(self.request.body)
                setattr(self, '_request_json', payload)
                return payload
            except JSONDecodeError:
                raise BadRequestError('body json is invalid')

    @staticmethod
    def _form_pipeline(form_class: Type[Form], data: Mapping):
        if form_class:
            form = form_class(data)
            if form.is_valid():
                return form.cleaned_data
            else:
                raise HttpFormError(form)

    def _query_form(self):
        self._request_query = self._form_pipeline(self.Meta.query_form,
                                                  self.request.GET)

    def _body_form(self):
        body_form = self.Meta.body_form
        if body_form:
            payload = self.get_request_json()
            self._request_body = self._form_pipeline(body_form, payload)

    def perform_request_pipelines(self):
        self._query_form()
        self._body_form()

    def _serializer_pipeline(self, response):
        if self.Meta.serializer:
            kwargs = self.get_serializer_kwargs()
            return self.Meta.serializer(**kwargs).dump(
                response,
                many=self.Meta.serializer_many
            )
        return response

    def get_serializer_kwargs(self):
        return {}

    @staticmethod
    def _generic_response(response):
        return {
            'status': 'ok',
            'data': response
        }

    @staticmethod
    def _json_response(response):
        return JsonResponse(data=response)

    def perform_response_pipelines(self, response):
        response = self._serializer_pipeline(response)
        response = self._generic_response(response)
        response = self._json_response(response)
        return response

    @staticmethod
    def _handle_http_error(e: HttpError) -> JsonResponse:
        return JsonResponse(
            status=e.http_code,
            data=e.get_dict()
        )

    def dispatch(self, request, *args, **kwargs):
        try:
            if request.method.lower() != self.Meta.method.value:
                raise HttpNotImplementedError
            self.perform_request_pipelines()
            response = self.execute(request, *args, **kwargs)
            return self.perform_response_pipelines(response)
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            if settings.DEBUG:
                raise e
            self.logger.exception(f'Unhandled exception on {self.request.path}')
            return self._handle_http_error(InternalServerError())

    dispatch.csrf_exempt = True

    def execute(self, request, *args, **kwargs):
        raise NotImplementedError
