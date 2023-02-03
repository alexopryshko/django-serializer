from typing import Sequence, Type, Union

import pytest
from django.core import checks
from django.forms import Form

from django_serializer.v2.exceptions import (
    IncorrectMetaException,
    BadRequestError,
)
from django_serializer.v2.serializer import Serializer
from django_serializer.v2.views import ApiView, HttpMethod


class TestMeta:
    @staticmethod
    def _create_view(attrs)  -> Type[ApiView]:
        class View(ApiView):
            class Meta:
                for k, v in attrs.items():
                    locals()[k] = v

        return View

    @staticmethod
    def _create_meta(attrs) -> Sequence[str]:
        try:
            TestMeta._create_view(attrs)
        except IncorrectMetaException as e:
            return e.errors

    def test_empty(self):
        errors = self._create_meta({})
        assert errors == ['`method` is required']

    def test_method(self):
        errors = self._create_meta({'tags': ['tags'], 'method': 'get'})
        assert errors == [
            '`method` has incorrect type, should be `<enum \'HttpMethod\'>`'
        ]

    @pytest.mark.parametrize('tags, expected_errors', [
        (None, [
            checks.Warning(
                f'`View.Meta.tags` variable has incorrect type {type(None)}',
                hint='View.Meta.tags should be list or tuple',
                id='django_serializer.meta.tags.W001'
            )
        ]),
        ([1], [
            checks.Warning(
                f'`View.Meta.tags[0]` variable has incorrect type {type(1)}',
                hint='View.Meta.tags[0] should be str',
                id='django_serializer.meta.tags.W002'
            )
        ]),
        (['t'], []),
    ])
    def test_tags(self, tags, expected_errors):
        view = self._create_view({'tags': tags, 'method': HttpMethod.GET})

        for error in expected_errors:
            error.obj = view
        assert view.check() == expected_errors

    @pytest.mark.parametrize('errors, expected_errors', [
        (None, [],),
        (1, [
            checks.Error(
                f'`View.Meta.errors` variable has incorrect type {type(1)}',
                hint='View.Meta.errors should be list or tuple',
                id='django_serializer.meta.errors.E001'
            )
        ]),
        ([Exception, 1], [
            checks.Error(
                f'`View.Meta.errors[0]` variable has incorrect type {type(Exception)}',
                hint='`View.Meta.errors[0]` should be subclass of django_serializer.v2.exceptions.http.HttpError',
                id='django_serializer.meta.errors.E002'
            ),
            checks.Error(
                f'`View.Meta.errors[1]` variable has incorrect type {type(1)}',
                hint='`View.Meta.errors[1]` should be subclass of django_serializer.v2.exceptions.http.HttpError',
                id='django_serializer.meta.errors.E002'
            )
        ]),
        ([BadRequestError], []),
    ])
    def test_errors(self, errors, expected_errors):
        view = self._create_view({'errors': errors, 'method': HttpMethod.GET})

        for error in expected_errors:
            error.obj = view
        assert view.check() == expected_errors

    @pytest.mark.parametrize('field, value, expected_errors', [
        ('summary', 1, ['`summary` has incorrect type, '
                        'should be `<class \'str\'>`']),
        ('summary', 's', None),

        ('description', 1, ['`description` has incorrect type, '
                            'should be `<class \'str\'>`']),
        ('description', 's', None),

        ('query_form', 1, ['`query_form` has incorrect type, '
                           'should be subclass of '
                           '`<class \'django.forms.forms.BaseForm\'>`']),
        ('query_form', Exception, ['`query_form` has incorrect type, '
                                   'should be subclass of '
                                   '`<class \'django.forms.forms.BaseForm\'>`']),
        ('query_form', Form, None),

        ('body_form', 1, ['`body_form` has incorrect type, '
                          'should be subclass of '
                          '`<class \'django.forms.forms.BaseForm\'>`']),
        ('body_form', Exception, ['`body_form` has incorrect type, '
                                  'should be subclass of '
                                  '`<class \'django.forms.forms.BaseForm\'>`']),
        ('body_form', Form, None),

        ('body_form', 1, ['`body_form` has incorrect type, '
                          'should be subclass of '
                          '`<class \'django.forms.forms.BaseForm\'>`']),
        ('body_form', Exception, ['`body_form` has incorrect type, '
                                  'should be subclass of '
                                  '`<class \'django.forms.forms.BaseForm\'>`']),
        ('body_form', Form, None),

        ('serializer', 1,
         ['`serializer` has incorrect type, '
          'should be subclass of `<class '
          "'django_serializer.v2.serializer.Serializer'>`"]),
        ('serializer', Exception,
         ['`serializer` has incorrect type, '
          'should be subclass of `<class '
          "'django_serializer.v2.serializer.Serializer'>`"]),
        ('serializer', Serializer, None),

        ('serializer_many', '1', ["`serializer_many` has incorrect type, "
                                  "should be `<class 'bool'>`"]),
        ('serializer_many', True, None),

    ])
    def test_var(self, field, value, expected_errors):
        errors = self._create_meta({'tags': ['tags'], 'method': HttpMethod.GET,
                                    field: value})
        assert errors == expected_errors
