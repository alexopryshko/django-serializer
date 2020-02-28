from typing import Type

from django.forms import Form

from django_serializer.v2.views import ApiView
from django_serializer.v2.views.meta import ApiViewMeta, HttpMethod


class CreateApiViewMeta(ApiViewMeta):
    class Meta(ApiViewMeta.Meta):
        method = HttpMethod.POST
        body_form: Type[Form] = None


class CreateApiView(ApiView, metaclass=CreateApiViewMeta, checkmeta=False):
    pass
