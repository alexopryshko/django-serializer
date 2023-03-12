from django import forms

from django_serializer.v2.serializer import Serializer
from django_serializer.v2.views import ApiView, HttpMethod
from marshmallow import fields


class GetView(ApiView):
    class Meta:
        tags = ['general']
        method = HttpMethod.GET

    def execute(self, request, *args, **kwargs):
        return {}


class GetQueryView(ApiView):
    class Meta:
        class QueryForm(forms.Form):
            q = forms.CharField()

        tags = ['general']
        method = HttpMethod.GET
        query_form = QueryForm

    def execute(self, request, *args, **kwargs):
        return self.request_query


class PostView(ApiView):
    class Meta:
        tags = ['general']
        method = HttpMethod.POST

    def execute(self, request, *args, **kwargs):
        return {}


class PostBodyView(ApiView):
    class Meta:
        class BodyForm(forms.Form):
            q = forms.CharField()

        tags = ['general']
        method = HttpMethod.POST
        body_form = BodyForm

    def execute(self, request, *args, **kwargs):
        return self.request_body


class InternalServerErrorView(ApiView):
    class Meta:
        tags = ['general']
        method = HttpMethod.GET

    def execute(self, request, *args, **kwargs):
        1/0


class TestSerializer(Serializer):
    a = fields.Int()


class SerializerView(ApiView):
    class Meta:
        tags = ['general']
        method = HttpMethod.GET
        serializer = TestSerializer

    def execute(self, request, *args, **kwargs):
        return {
            'a': '1',
            'b': 1
        }


class SerializerManyView(ApiView):
    class Meta:
        tags = ['general']
        method = HttpMethod.GET
        serializer = TestSerializer
        serializer_many = True

    def execute(self, request, *args, **kwargs):
        return [{
            'a': '1',
            'b': 1
        }]
