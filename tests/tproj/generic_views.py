from django import forms

from django_serializer.v2.exceptions import BadRequestError, NotFoundError
from django_serializer.v2.serializer import ModelSerializer, Serializer, fields
from django_serializer.v2.views import (
    CreateApiView,
    GetApiView,
    UpdateApiView,
    DeleteApiView,
    ListApiView,
)
from django_serializer.v2.views.paginator import AscFromIdPaginator, LimitOffsetPaginator
from tests.tproj.app.models import SomeModel


class SomeModelForm(forms.ModelForm):
    class Meta:
        model = SomeModel
        fields = '__all__'


class SomeModelSerializer(ModelSerializer):
    class SMeta:
        model = SomeModel


class SomeModelCreateView(CreateApiView):
    class Meta:
        tags = ['create']
        model_form = SomeModelForm
        serializer = SomeModelSerializer


class SomeModelGetView(GetApiView):
    class Meta:
        tags = ['get']
        model = SomeModel
        errors = [BadRequestError, NotFoundError, ]
        serializer = SomeModelSerializer

    def has_permissions(self, obj: SomeModel) -> bool:
        # some condition to check permission for operation
        return obj.nullable != 'without_permissions'


class SomeModelUpdateView(UpdateApiView):
    class Meta:
        tags = ['update']
        model = SomeModel
        model_form = SomeModelForm
        serializer = SomeModelSerializer

    def has_permissions(self, obj: SomeModel) -> bool:
        # some condition to check permission for operation
        return obj.nullable != 'without_permissions'


class SomeModelDeleteView(DeleteApiView):
    class Meta:
        tags = ['update']
        model = SomeModel

    def has_permissions(self, obj: SomeModel) -> bool:
        # some condition to check permission for operation
        return obj.nullable != 'without_permissions'


class SimpleListApiView(ListApiView):
    class Meta:
        tags = ['list']
        model = SomeModel
        serializer = SomeModelSerializer


class ListSomeModelSerializer(Serializer):
    list = fields.Nested(SomeModelSerializer, many=True)
    count = fields.Int()


class PaginateListApiView(ListApiView):
    class Meta:
        tags = ['list']
        model = SomeModel
        serializer = ListSomeModelSerializer
        serializer_many = False
        paginator = AscFromIdPaginator

    def build_response(self, qs, qs_after_paginator=None):
        return {
            'count': qs.count(),
            'list': qs_after_paginator
        }


class LimitOffsetPaginateListApiView(ListApiView):
    class Meta:
        tags = ['list']
        model = SomeModel
        serializer = SomeModelSerializer
        paginator = LimitOffsetPaginator
