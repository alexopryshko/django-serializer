from typing import Type

from django import forms

from django_serializer.v2.views import ApiView


class Paginator:
    form: Type[forms.Form] = None

    def __init__(self, view: ApiView):
        self.view: ApiView = view
        self.data = None

    def validate_form(self):
        self.data = self.view._form_pipeline(self.form, self.view.request.GET)

    def paginate(self, qs):
        raise NotImplementedError


class FromIdPaginator(Paginator):
    class FromIdForm(forms.Form):
        from_id = forms.IntegerField(min_value=1, required=False)
        limit = forms.IntegerField(min_value=1, max_value=100, required=False)

    default_limit = 10
    condition_kwarg = None
    form = FromIdForm

    def paginate(self, qs):
        from_id = self.data['from_id']
        limit = self.data['limit'] or self.default_limit
        if from_id:
            qs = qs.filter(**{self.condition_kwarg: from_id})
        return qs[:limit]


class AscFromIdPaginator(FromIdPaginator):
    condition_kwarg = 'id__gt'


class DescFromIdPaginator(FromIdPaginator):
    condition_kwarg = 'id__lt'
