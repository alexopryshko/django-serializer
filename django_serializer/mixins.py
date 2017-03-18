from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django_serializer.exceptions import ServerError


class CsrfExemptMixin:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ObjectMixin:
    model = None

    class ObjectForm(forms.Form):
        id = forms.IntegerField()

    def get_args_form(self):
        return self.ObjectForm

    def get_object(self):
        try:
            return self.model.objects.get(pk=self.request_args['id'])
        except self.model.DoesNotExist:
            raise ServerError(ServerError.NOT_FOUND)
        except (ValueError, KeyError):
            raise ServerError(ServerError.BAD_REQUEST)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs


class SerializerMixin:
    serializer = None

    def get_serializer_class(self, obj=None):
        return self.serializer

    def get_serializer_kwargs(self, obj, **kwargs):
        serializer_kwargs = {
            'obj': obj
        }
        serializer_kwargs.update(kwargs)
        return serializer_kwargs

    def get_serializer(self, obj, **kwargs):
        serializer_class = self.get_serializer_class(obj)
        return serializer_class(**self.get_serializer_kwargs(obj, **kwargs))

    def response_middleware(self, response):
        if self.get_serializer_class(response):
            serializer = self.get_serializer(response)
            response = serializer.serialize()
        return response


class FormMixin:
    form_class = None

    def get_form_kwargs(self):
        kwargs = {
            'data': self.request.GET,
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request_body,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form_class(self):
        return self.form_class

    def get_form(self):
        """
        Returns an instance of the form to be used in this view.
        """
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())


class ListMixin:
    model = None
    paginator = None

    def get_paginator_class(self):
        return self.paginator

    def get_paginator_kwargs(self):
        return {
            'object_list': self.get_queryset(),
            'arguments': self.request.GET
        }

    def get_paginator(self):
        if hasattr(self, '_paginator'):
            return getattr(self, '_paginator')
        if self.paginator:
            setattr(self, '_paginator', self.get_paginator_class()(**self.get_paginator_kwargs()))
            return getattr(self, '_paginator')

    def get_queryset(self):
        return self.model.objects.all().order_by('id')

    def get_serializer_kwargs(self, obj, **kwargs):
        return super().get_serializer_kwargs(obj, **{'multiple': True})

    def response_middleware(self, response):
        response = super().response_middleware(response)
        paginator = self.get_paginator()
        if paginator:
            response = {
                'count': self.get_paginator().count,
                'list': response
            }
        return response
