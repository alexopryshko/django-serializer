from django import forms

from django_serializer.exceptions import FormException


class Paginator(object):
    form = None

    def __init__(self, object_list, arguments):
        self.object_list = object_list
        self._arguments = arguments
        self._count = None
        self.validated_arguments = None

    def get_form(self):
        return self.get_form_class()(**self.get_form_kwargs())

    def get_form_class(self):
        return self.form

    def get_form_kwargs(self):
        return {'data': self._arguments}

    def validate_arguments(self):
        form = self.get_form()
        if form.is_valid():
            self.validated_arguments = form.cleaned_data
        else:
            raise FormException(form)

    def _get_count(self):
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

    def page(self):
        if self.validated_arguments is None:
            self.validate_arguments()


class LimitOffsetPaginator(Paginator):
    LIMIT = 20
    OFFSET = 0

    class LimitOffsetForm(forms.Form):
        limit = forms.IntegerField(min_value=1, max_value=100, required=False)
        offset = forms.IntegerField(min_value=0, required=False)

    form = LimitOffsetForm

    def page(self):
        super().page()
        bottom = self.validated_arguments['offset'] or self.OFFSET
        top = bottom + (self.validated_arguments['limit'] or self.LIMIT)
        return self.object_list[bottom:top]
