import pytest
from django.forms import Form

from django_serializer.v2.exceptions import (
    IncorrectMetaException,
    BadRequestError,
)
from django_serializer.v2.serializer import Serializer
from django_serializer.v2.views import ApiView, HttpMethod


class TestMeta:
    @staticmethod
    def _create_meta(attrs):
        try:
            class View(ApiView):
                class Meta:
                    for k, v in attrs.items():
                        locals()[k] = v
        except IncorrectMetaException as e:
            return e.errors

    def test_empty(self):
        errors = self._create_meta({})
        assert errors == ['`tags` is required', '`method` is required']

    def test_method(self):
        errors = self._create_meta({'tags': ['tags'], 'method': 'get'})
        assert errors == [
            '`method` has incorrect type, should be `<enum \'HttpMethod\'>`'
        ]

    @pytest.mark.parametrize('tags, expected_errors', [
        (None, ['`tags` is required']),
        ([], ['`tags` is required']),
        ([1], ['`tags` item has incorrect type, should be str']),
        (['t'], None),
    ])
    def test_tags(self, tags, expected_errors):
        errors = self._create_meta({'tags': tags, 'method': HttpMethod.GET})
        assert errors == expected_errors

    @pytest.mark.parametrize('field, value, expected_errors', [
        ('summary', 1, ['`summary` has incorrect type, '
                        'should be `<class \'str\'>`']),
        ('summary', 's', None),

        ('description', 1, ['`description` has incorrect type, '
                            'should be `<class \'str\'>`']),
        ('description', 's', None),

        ('query_form', 1, ['`query_form` has incorrect type, '
                           'should be subclass of '
                           '`<class \'django.forms.forms.Form\'>`']),
        ('query_form', Exception, ['`query_form` has incorrect type, '
                                   'should be subclass of '
                                   '`<class \'django.forms.forms.Form\'>`']),
        ('query_form', Form, None),

        ('body_form', 1, ['`body_form` has incorrect type, '
                          'should be subclass of '
                          '`<class \'django.forms.forms.Form\'>`']),
        ('body_form', Exception, ['`body_form` has incorrect type, '
                                  'should be subclass of '
                                  '`<class \'django.forms.forms.Form\'>`']),
        ('body_form', Form, None),

        ('body_form', 1, ['`body_form` has incorrect type, '
                          'should be subclass of '
                          '`<class \'django.forms.forms.Form\'>`']),
        ('body_form', Exception, ['`body_form` has incorrect type, '
                                  'should be subclass of '
                                  '`<class \'django.forms.forms.Form\'>`']),
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

        ('errors', [Exception, 1], ['`errors` item has incorrect type, '
                                    'should be subtype of HttpError']),
        ('errors', [BadRequestError], None),
    ])
    def test_var(self, field, value, expected_errors):
        errors = self._create_meta({'tags': ['tags'], 'method': HttpMethod.GET,
                                    field: value})
        assert errors == expected_errors
