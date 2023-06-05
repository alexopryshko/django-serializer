from math import ceil, floor
from typing import Collection, Optional, Type, Union
from warnings import warn

from django import forms
from django.db.models import QuerySet

from django_serializer.v2.views import ApiView

deprecated_names = [("Paginator", "BasePaginator")]


class BasePaginator:
    form: Type[forms.Form] = None

    def __init__(self, view: ApiView, qs: Optional[Union[Collection, QuerySet]] = None):
        self.view: ApiView = view
        self._queryset = qs
        self.data = None
        self._count = None

        if self._queryset is None:
            warn(
                (
                    "`qs` argument will become mandatory in the future. "
                    "`total_count` method may not work properly without `_queryset`"
                ),
                FutureWarning,
                stacklevel=2,
            )

    @property
    def total_count(self) -> int:
        if self._count is None:
            try:
                self._count = self._get_queryset().count()
            except (AttributeError, TypeError):
                self._count = len(self._get_queryset())
        return self._count

    def _get_queryset(
        self, qs: Optional[Union[Collection, QuerySet]] = None
    ) -> Union[Collection, QuerySet]:
        if self._queryset is None:
            self._queryset = qs
        return self._queryset

    def validate_form(self):
        self.data = self.view._form_pipeline(self.form, self.view.request.GET)

    def paginate(self, qs: Optional[Union[Collection, QuerySet]] = None):
        raise NotImplementedError


class FromIdPaginator(BasePaginator):
    class FromIdForm(forms.Form):
        from_id = forms.IntegerField(min_value=1, required=False)
        limit = forms.IntegerField(min_value=1, max_value=100, required=False)

    default_limit = 10
    condition_kwarg = None
    form = FromIdForm

    def _get_limit(self) -> int:
        return self.data["limit"] or self.default_limit

    def paginate(self, qs: Optional[QuerySet] = None) -> QuerySet:
        from_id = self.data["from_id"]
        limit = self._get_limit()
        queryset = self._get_queryset(qs)
        if from_id:
            queryset = queryset.filter(**{self.condition_kwarg: from_id})
        return queryset[:limit]


class AscFromIdPaginator(FromIdPaginator):
    condition_kwarg = "id__gt"


class DescFromIdPaginator(FromIdPaginator):
    condition_kwarg = "id__lt"


class LimitOffsetPaginator(BasePaginator):
    class LimitOffsetPaginatorForm(forms.Form):
        limit = forms.IntegerField(min_value=1, max_value=100, required=False)
        offset = forms.IntegerField(min_value=0, required=False)
        all = forms.BooleanField(required=False)

    default_limit = 20
    default_offset = 0
    form = LimitOffsetPaginatorForm

    @property
    def current_page(self) -> int:
        """
        Calculate the current page number using given limit,
        offset and qs total_count. If offset value is greater
        than total_count: returns -1.
        """
        if not self.total_count:
            return 0
        limit = self._get_limit()
        offset = self._get_offset()
        if offset >= self.total_count:
            return -1
        try:
            return floor(offset / limit) + 1
        except (TypeError, ZeroDivisionError):
            return 1

    @property
    def pages_total_count(self) -> int:
        """Calculate the total number of pages."""
        if not self.total_count:
            return 0
        try:
            return ceil(self.total_count / self._get_limit())
        except (TypeError, ZeroDivisionError):
            return 1

    def _get_limit(self) -> int:
        if self.data["all"]:
            return self.total_count
        return self.data["limit"] or self.default_limit

    def _get_offset(self) -> int:
        if self.data["all"]:
            return 0
        return self.data["offset"] or self.default_offset

    def paginate(
        self, qs: Optional[Union[Collection, QuerySet]] = None
    ) -> Union[Collection, QuerySet]:
        queryset = self._get_queryset(qs)
        if self.data["all"]:
            return queryset
        limit = self._get_limit()
        offset = self._get_offset()
        return queryset[offset : limit + offset]


def __getattr__(name):
    for old_name, new_name in deprecated_names:
        if name == old_name:
            warn(
                f"The '{old_name}' class or function is renamed '{new_name}'",
                DeprecationWarning,
                stacklevel=2,
            )
            return globals()[new_name]
    raise AttributeError(f"module {__name__} has no attribute {name}")
