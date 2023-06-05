import logging
from typing import Mapping, Type

from django.conf import settings
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse
from django.views import View

from django_serializer.v2.exceptions import (
    BadRequestError,
    HttpError,
    HttpFormError,
    HttpNotImplementedError,
    InternalServerError,
    ParseException,
)
from django_serializer.v2.renderers import BaseRenderer
from django_serializer.v2.serializer import Serializer
from django_serializer.v2.views.meta import ApiViewMeta

__all__ = ("ApiView",)


class ApiView(View, metaclass=ApiViewMeta, checkmeta=False):
    """
    Base class to work with django-serializer.

    Provides base functionality for request processing.
    """

    Meta = ApiViewMeta.Meta

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(
            f"django_serializer.views.{self.__class__.__name__}"
        )

    @property
    def logger(self) -> logging.Logger:
        """
        Use this logger inside view processes.
        You can also turn it off via logging settings.

        :return: logger
        :rtype: logging.Logger
        """
        return self._logger

    @property
    def request_query(self) -> Mapping:
        """
        Property to access request.GET parameters
        :return: dict
        """
        return getattr(self, "_request_query", None)

    @property
    def request_body(self) -> Mapping:
        """
        Property to access request.body parameters. request.body parsed by Meta.Parser

        :return: dict
        """
        return getattr(self, "_request_body", None)

    def get_parser(self):
        return self.Meta.body_parser()

    def get_request_json(self, request: HttpRequest):
        if hasattr(self, "_request_json"):
            return getattr(self, "_request_json")
        if "application/json" in request.content_type:
            try:
                parser = self.get_parser()
                payload = parser.parse(request.body)
                setattr(self, "_request_json", payload)
                return payload
            except ParseException:
                raise BadRequestError("body json is invalid")

    @staticmethod
    def _form_pipeline(form_class: Type[BaseForm], data: Mapping):
        if form_class:
            form = form_class(data)
            if form.is_valid():
                return form.cleaned_data
            else:
                raise HttpFormError(form)

    def _query_form(self, request: HttpRequest):
        self._request_query = self._form_pipeline(self.Meta.query_form, request.GET)

    def _body_form(self, request: HttpRequest):
        body_form = self.Meta.body_form
        if body_form:
            payload = self.get_request_json(request)
            self._request_body = self._form_pipeline(body_form, payload)

    def _check_request_method(self, request: HttpRequest):
        """
        Check request method is allowed
        :param request: HttpRequest
        :return: None
        """
        if request.method.lower() != self.Meta.method.value:
            raise HttpNotImplementedError

    def _check_section_permission(self, request: HttpRequest):
        """
        Used to validate user has permission to access section.
        For example, check authorization and raise error if not allowed
        :param request: HttpRequest
        :return: None
        """
        pass

    def perform_request_pipelines(self, request: HttpRequest):
        self._check_request_method(request)
        self._check_section_permission(request)
        self._query_form(request)
        self._body_form(request)

    def get_serializer_class(self) -> Type[Serializer]:
        """
        Default implementation returns class defined in Meta.serializer

        You can override for custom Serializer getter logic.
        It is not recommended as it will break swagger generation.

        :return: serializer class
        :rtype: django_serializer.v2.serializer.Serializer
        """
        return self.Meta.serializer

    def get_serializer_kwargs(self) -> dict:
        """
        Default implementation adds request to the serializer context

        Override this to add extra context or kwargs for the serializer

        :return: dictionary passed to serializer as kwargs
        :rtype: dict
        """
        return {"context": {"request": self.request}, "many": self.Meta.serializer_many}

    def get_serializer(self) -> Serializer:
        """
        Instantiates serializer

        :return: serializer object
        :rtype: Serializer
        """
        serializer_class = self.get_serializer_class()
        if serializer_class:
            serializer_kwargs = self.get_serializer_kwargs()
            return serializer_class(**serializer_kwargs)

    def _serializer_pipeline(self, response):
        serializer = self.get_serializer()
        if serializer:
            return serializer.dump(response)
        return response

    def _generic_response(self, response):
        return {"status": "ok", "data": response}

    def get_renderer_class(self, request) -> Type[BaseRenderer]:
        return self.Meta.renderer

    def get_renderer(self, request) -> BaseRenderer:
        return self.get_renderer_class(request)()

    def render_response(self, request: HttpRequest, response) -> HttpResponse:
        """
        Renders object returned from previous stages to HttpResponse

        :param request: HttpRequest passed from dispatch
        :param response: dict object returned from serializer or execute stage.
        :return: HttpResponse returned to user
        :rtype HttpResponse
        """
        renderer = self.get_renderer(request)
        return renderer.render(response)

    def perform_response_pipelines(self, request: HttpRequest, response):
        response = self._serializer_pipeline(response)
        response = self._generic_response(response)
        response = self.render_response(request, response)
        return response

    def handle_http_error(self, request: HttpRequest, e: HttpError) -> HttpResponse:
        """
        HttpError handler. Can be overriden if needed.

        :param request: HttpRequest passed from dispatch
        :param e: HttpError
        :return: HttpResponse returned to user
        :rtype: HttpResponse
        """
        response = self.render_response(request, e.get_dict())
        response.status_code = e.http_code
        return response

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        try:
            self.perform_request_pipelines(request)
            response = self.execute(request, *args, **kwargs)
            return self.perform_response_pipelines(request, response)
        except HttpError as e:
            return self.handle_http_error(request, e)
        except Exception as e:
            if settings.DEBUG:
                raise e
            self.logger.exception(f"Unhandled exception on {self.request.path}")
            return self.handle_http_error(request, InternalServerError())

    dispatch.csrf_exempt = True

    def execute(self, request, *args, **kwargs):
        """
        Contains view logic. Override me in subclass

        :param request: passed from dispatch
        :param args: passed from dispatch
        :param kwargs: passed from dispatch
        :return: Any serializable object
        :rtype: dict
        """
        raise NotImplementedError
