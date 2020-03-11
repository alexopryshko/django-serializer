from django import forms
from marshmallow import fields as f

from django_serializer.v2.swagger.utils import form2schema
from tests.tproj.generic_views import SomeModelGetView, SomeModelCreateView, \
    SomeModelUpdateView, SomeModelDeleteView, PaginateListApiView
from tests.tproj.urls import urlpatterns


class TestSwagger:
    def test_form2schema(self):
        class Form(forms.Form):
            i = forms.IntegerField()
            i_not_required = forms.IntegerField(required=False)
            f = forms.FloatField()
            dec = forms.DecimalField()
            b = forms.BooleanField()
            c = forms.CharField()
            d = forms.DateField()
            dt = forms.DateTimeField()
            e = forms.EmailField()
            u = forms.URLField()

        schema = form2schema(Form)
        assert str(schema.declared_fields['i']) == str(f.Integer(required=True))
        assert str(schema.declared_fields['f']) == str(f.Float(required=True))
        assert str(schema.declared_fields['dec']) == \
               str(f.Decimal(required=True))

        assert str(schema.declared_fields['b']) == str(f.Boolean(required=True))
        assert str(schema.declared_fields['c']) == str(f.String(required=True))
        assert str(schema.declared_fields['e']) == str(f.Email(required=True))
        assert str(schema.declared_fields['u']) == str(f.Url(required=True))

        assert str(schema.declared_fields['d']) == str(f.Date(required=True))
        assert str(schema.declared_fields['dt']) == \
               str(f.DateTime(required=True))

        assert str(schema.declared_fields['i_not_required']) == str(
            f.Integer(required=False))

    def test_swagger(self, client):
        resp = client.get('/swagger.json')
        json = resp.json()
        assert sorted(list(json['components']['schemas'].keys())) == sorted([
            'ListSomeModelSerializer', 'SomeModelSerializer', 'TestSerializer',
            'BadRequest', 'NotFound'
        ])
        assert sorted(list(json['paths'].keys()) + ['/swagger.json']) == \
               sorted(list(map(lambda path: f'/{path.pattern._route}',
                               urlpatterns)))

    def test_get_view(self, client):
        resp = client.get('/swagger.json')
        path = resp.json()['paths']['/get_model']['get']
        path_parameters = path['parameters']
        path_responses = path['responses']
        path_tags = path['tags']

        assert len(path_parameters) == 1
        assert path_parameters[0]['in'] == 'query'
        assert path_parameters[0]['name'] == 'id'
        assert path_parameters[0]['required'] is True

        assert sorted(list(path_responses.keys())) == ['200', '400', '404']
        assert path_responses['200']['content']['application/json']['schema'][
                   '$ref'] == '#/components/schemas/SomeModelSerializer'

        assert path_tags == SomeModelGetView.Meta.tags

    def test_create_view(self, client):
        resp = client.get('/swagger.json')
        path = resp.json()['paths']['/create']['post']
        path_body = path['requestBody']['content']['application/json']['schema']
        path_responses = path['responses']
        path_tags = path['tags']
        assert sorted(list(path_body['properties'].keys())) == ['f', 'i',
                                                                'nullable']

        assert len(path_responses.keys()) == 1
        assert path_responses['200']['content']['application/json']['schema'][
                   '$ref'] == '#/components/schemas/SomeModelSerializer'

        assert path_tags == SomeModelCreateView.Meta.tags

    def test_update_view(self, client):
        resp = client.get('/swagger.json')
        path = resp.json()['paths']['/update']['post']
        path_body = path['requestBody']['content']['application/json']['schema']
        path_responses = path['responses']
        path_tags = path['tags']

        assert sorted(list(path_body['properties'].keys())) == ['f', 'i', 'id',
                                                                'nullable']

        assert len(path_responses.keys()) == 1
        assert path_responses['200']['content']['application/json']['schema'][
                   '$ref'] == '#/components/schemas/SomeModelSerializer'

        assert path_tags == SomeModelUpdateView.Meta.tags

    def test_delete_view(self, client):
        resp = client.get('/swagger.json')
        path = resp.json()['paths']['/delete']['post']
        path_body = path['requestBody']['content']['application/json']['schema']
        path_responses = path['responses']
        path_tags = path['tags']

        assert sorted(list(path_body['properties'].keys())) == ['id']
        assert path_responses['200']['description'] == 'success'
        assert path_tags == SomeModelDeleteView.Meta.tags

    def test_paginate_list_view(self, client):
        resp = client.get('/swagger.json')
        path = resp.json()['paths']['/paginate_list']['get']
        path_parameters = path['parameters']
        path_responses = path['responses']
        path_tags = path['tags']

        assert sorted(list(map(lambda i: i['name'], path_parameters))) == \
               ['from_id', 'limit']

        assert len(path_responses.keys()) == 1
        assert path_responses['200']['content']['application/json']['schema'][
                   '$ref'] == '#/components/schemas/ListSomeModelSerializer'

        assert path_tags == PaginateListApiView.Meta.tags
