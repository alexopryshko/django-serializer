from typing import Type, Optional

from django import forms
from django.db.models import Model

from django_serializer.v2.exceptions import HttpFormError, ForbiddenError
from django_serializer.v2.serializer import Serializer
from django_serializer.v2.views import ApiView
from django_serializer.v2.views.meta import ApiViewMeta, HttpMethod
from django_serializer.v2.views.mixins import (
    FormMixin,
    ObjectMixin,
    CheckPermissionsMixin,
)
from django_serializer.v2.views.paginator import Paginator

__all__ = (
    'CreateApiView', 'GetApiView', 'UpdateApiView', 'DeleteApiView',
    'ListApiView',
)


class CreateApiViewMeta(ApiViewMeta):
    class Meta(ApiViewMeta.Meta):
        method: HttpMethod = HttpMethod.POST
        model_form: Type[forms.ModelForm] = None
        serializer: Type[Serializer] = None


class CreateApiView(CheckPermissionsMixin, FormMixin, ApiView,
                    metaclass=CreateApiViewMeta, checkmeta=False):
    Meta = CreateApiViewMeta.Meta

    def has_permissions(self) -> bool:
        return True

    def execute(self, request, *args, **kwargs):
        self.check_permissions()
        form = self.get_form()
        if form.is_valid():
            instance = form.save()
        else:
            raise HttpFormError(form)
        return instance


class GetApiForm(forms.Form):
    id = forms.IntegerField()


class GetApiViewMeta(ApiViewMeta):
    class Meta(ApiViewMeta.Meta):
        method: HttpMethod = HttpMethod.GET
        model: Type[Model] = None
        query_form: Type[forms.Form] = GetApiForm
        object_key: str = 'id'
        serializer: Type[Serializer] = None


class GetApiView(CheckPermissionsMixin, ObjectMixin, ApiView,
                 metaclass=GetApiViewMeta, checkmeta=False):
    Meta = GetApiViewMeta.Meta

    def get_object(self):
        m: Type[Model] = self.Meta.model
        key: str = self.Meta.object_key
        return m.objects.get(**{key: self.request_query[key]})

    def has_permissions(self, obj: Model) -> bool:
        return True

    def execute(self, request, *args, **kwargs):
        obj = self._get_object()
        self.check_permissions(obj=obj)
        return obj


class UpdateApiViewMeta(ApiViewMeta):
    class Meta(ApiViewMeta.Meta):
        method: HttpMethod = HttpMethod.POST
        body_form: Type[forms.BaseForm] = GetApiForm
        model: Type[Model] = None
        model_form: Type[forms.ModelForm] = None
        object_key: str = 'id'
        serializer: Type[Serializer] = None


class UpdateApiView(ObjectMixin, FormMixin, ApiView,
                    metaclass=UpdateApiViewMeta, checkmeta=False):
    Meta = UpdateApiViewMeta.Meta

    def has_permissions(self, obj: Model) -> bool:
        return True

    def execute(self, request, *args, **kwargs):
        obj = self._get_object()
        if not self.has_permissions(obj):
            raise ForbiddenError
        form = self.get_form()
        if form.is_valid():
            instance = form.save()
        else:
            raise HttpFormError(form)
        return instance


class DeleteApiViewMeta(ApiViewMeta):
    class Meta(ApiViewMeta.Meta):
        method: HttpMethod = HttpMethod.POST
        body_form: Type[forms.BaseForm] = GetApiForm
        model: Type[Model] = None
        object_key: str = 'id'


class DeleteApiView(CheckPermissionsMixin, ObjectMixin, ApiView,
                    metaclass=DeleteApiViewMeta, checkmeta=False):
    Meta = DeleteApiViewMeta.Meta

    def has_permissions(self, obj: Model) -> bool:
        return True

    def execute(self, request, *args, **kwargs):
        obj = self._get_object()
        self.check_permissions(obj=obj)
        obj.delete()
        return {}


class ListApiViewMeta(ApiViewMeta):
    class Meta(ApiViewMeta.Meta):
        method: HttpMethod = HttpMethod.GET
        model: Type[Model] = None
        serializer: Type[Serializer] = None
        serializer_many: bool = True
        paginator: Optional[Type[Paginator]] = None
        ordering: tuple = ('id',)


class ListApiView(CheckPermissionsMixin, ApiView,
                  metaclass=ListApiViewMeta, checkmeta=False):
    Meta = ListApiViewMeta.Meta

    def has_permissions(self) -> bool:
        return True

    def get_queryset(self):
        return self.Meta.model.objects.all().order_by(*self.Meta.ordering)

    def build_response(self, qs, qs_after_paginator=None):
        if qs_after_paginator is None:
            return qs
        return qs_after_paginator

    def execute(self, request, *args, **kwargs):
        self.check_permissions()
        qs = self.get_queryset()
        qs_after_paginator = None
        if self.Meta.paginator:
            paginator = self.Meta.paginator(self)
            paginator.validate_form()
            qs_after_paginator = paginator.paginate(qs)
        return self.build_response(
            qs=qs,
            qs_after_paginator=qs_after_paginator
        )
