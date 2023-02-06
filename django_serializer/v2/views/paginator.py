from typing import Collection, Iterable, Type, Union

from django import forms
from django.db.models import QuerySet

from django_serializer.v2.views import ApiView


class Paginator:
    form: Type[forms.Form] = None

    def __init__(self, view: ApiView):
        self.view: ApiView = view
        self.data = None

    def validate_form(self):
        self.data = self.view._form_pipeline(self.form, self.view.request.GET)

    def paginate(self, qs: Union[Collection, QuerySet]):
        raise NotImplementedError


class LimitOffsetPaginator(Paginator):
    class LimitOffsetPaginatorForm(forms.Form):
        limit = forms.IntegerField(min_value=1, max_value=100, required=False)
        offset = forms.IntegerField(min_value=0, required=False)
        all = forms.BooleanField(required=False)

    default_limit = 20
    default_offset = 0
    form = LimitOffsetPaginatorForm

    def paginate(self, qs):
        if self.data["all"]:
            return qs

        limit = self.data["limit"] or self.default_limit
        offset = self.data["offset"] or self.default_offset
        return qs[offset : limit + offset]


class FromIdPaginator(Paginator):
    class FromIdForm(forms.Form):
        from_id = forms.IntegerField(min_value=1, required=False)
        limit = forms.IntegerField(min_value=1, max_value=100, required=False)

    default_limit = 10
    condition_kwarg = None
    form = FromIdForm

    def paginate(self, qs: QuerySet):
        from_id = self.data['from_id']
        limit = self.data['limit'] or self.default_limit
        if from_id:
            qs = qs.filter(**{self.condition_kwarg: from_id})
        return qs[:limit]


class AscFromIdPaginator(FromIdPaginator):
    condition_kwarg = 'id__gt'


class DescFromIdPaginator(FromIdPaginator):
    condition_kwarg = 'id__lt'
