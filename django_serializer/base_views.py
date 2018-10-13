import json

from django.http import HttpResponse
from django.views.generic import View

from django_serializer.permissions import PermissionsMixin
from django_serializer.exceptions import (FormException, ServerError, )
from django_serializer.exceptions import BaseViewException as BVE_1
from django_serializer.exceptions import BaseViewException as BVE_2
from django_serializer.mixins import (
    CsrfExemptMixin,
    SerializerMixin,
    ObjectMixin,
    FormMixin,
    ListMixin,
)


class BaseView(View):
    args_form = None

    @property
    def request_args(self):
        return getattr(self, '_request_args', {})

    def get_args_form(self):
        return self.args_form

    @property
    def request_body(self):
        if hasattr(self, '_request_body'):
            return getattr(self, '_request_body')
        try:
            data = json.loads(self.request.body.decode('utf-8'))
        except Exception:
            data = {}
        setattr(self, '_request_body', data)
        return data

    def clean_args(self):
        if not self.get_args_form():
            return
        if hasattr(self, '_request_args'):
            return

        kwargs = {'data': self.request.GET}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({'data': self.request_body})
        form = self.get_args_form()(**kwargs)

        if form.is_valid():
            setattr(self, '_request_args', form.cleaned_data)
        else:
            raise FormException(form)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.clean_args()
            response = super().dispatch(request, *args, **kwargs)
            response = self.response_middleware(response)
            return self.response_wrapper(response)
        except (BVE_1, BVE_2) as e:
            return self.exception_wrapper(e)

    def response_middleware(self, response):
        return response

    def response_wrapper(self, response):
        return HttpResponse(json.dumps({'status': 'ok', 'data': response}), content_type="application/json")

    @staticmethod
    def exception_wrapper(exception):
        response = {
            'status': exception.get_alias(),
            'message': exception.get_description(),
            'data': {}
        }
        if exception.get_field_problems():
            response['field_problems'] = exception.get_field_problems()
        http_code = exception.get_http_code()
        return HttpResponse(json.dumps(response), content_type="application/json", status=http_code)

    def get(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def post(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def put(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def patch(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def delete(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def head(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def options(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)

    def trace(self, *args, **kwargs):
        raise ServerError(ServerError.NOT_IMPLEMENTED)


class CreateView(CsrfExemptMixin, PermissionsMixin, FormMixin, SerializerMixin, BaseView):
    def post(self, request, *args, **kwargs):
        self.check_w_permission(self.request.user)
        form = self.get_form()
        if form.is_valid():
            instance = form.save()
        else:
            raise FormException(form)
        return instance


class DetailsView(CsrfExemptMixin, PermissionsMixin, ObjectMixin, FormMixin, SerializerMixin, BaseView):
    def get(self, request, *args, **kwargs):
        self.check_r_permission(self.request.user)
        return self.get_object()

    def post(self, request, *args, **kwargs):
        self.check_w_permission(self.request.user)
        form = self.get_form()
        if form.is_valid():
            instance = form.save()
        else:
            raise FormException(form)
        return instance


class DeleteView(CsrfExemptMixin, PermissionsMixin, ObjectMixin, BaseView):
    def post(self, request, *args, **kwargs):
        self.check_d_permission(self.request.user)
        instance = self.get_object()
        instance.delete()
        return {}


class ListView(CsrfExemptMixin, PermissionsMixin, ListMixin, SerializerMixin, BaseView):
    def get(self, request, *args, **kwargs):
        self.check_r_permission(self.request.user)
        paginator = self.get_paginator()
        if paginator:
            instances = paginator.page()
        else:
            instances = self.get_queryset()
        return instances

