import copy
import enum
import inspect
import sys
from typing import Optional, List, Type, Union

from django.forms import BaseForm

from django_serializer.v2.exceptions import IncorrectMetaException, HttpError
from django_serializer.v2.serializer import Serializer


class HttpMethod(enum.Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    PATCH = 'patch'
    DELETE = 'delete'
    HEAD = 'head'
    OPTIONS = 'options'
    TRACE = 'trace'


class ApiViewMeta(type):
    class Meta:
        method: HttpMethod = None
        tags: List[str] = []
        summary: Optional[str] = None
        description: Optional[str] = None
        query_form: Optional[Type[BaseForm]] = None
        body_form: Optional[Type[BaseForm]] = None
        serializer: Optional[Type[Serializer]] = None
        serializer_many: bool = False
        errors: List[Type[HttpError]] = []

        __manual_validation__: List[str] = ['tags', 'errors']

    def __new__(mcs, name, bases, attrs, *args, **kwargs):
        checkmeta = kwargs.pop('checkmeta', True)
        # noinspection PyArgumentList
        cls = super().__new__(mcs, name, bases, attrs, *args, **kwargs)

        if checkmeta:
            options = attrs.get('Meta')
            base_options = mcs.find_base_options(bases)
            meta = mcs.merge_options(options, base_options)
            errors = []
            mcs.check_meta_extra(meta, errors)
            mj, mn = sys.version_info[:2]
            if mj >= 3 and mn >= 7:
                mcs.check_meta(meta, errors)
            if errors:
                raise IncorrectMetaException(name, errors)
            attrs['Meta'] = meta

        return cls

    @staticmethod
    def find_base_options(bases):
        for b in reversed(bases):
            options = getattr(b, 'Meta', None)
            if options is not None:
                return options

    @staticmethod
    def merge_options(options, base_options):
        if options is None:
            return base_options
        elif base_options is None:
            return options

        members = inspect.getmembers(base_options)
        for name, obj in members:
            if name.startswith('_'):
                continue
            setattr(options, name, copy.copy(getattr(options, name, obj)))

        return options

    @staticmethod
    def get_annotation(base_cls, name):
        for cls in base_cls.__mro__:
            if hasattr(cls, '__annotations__'):
                annt = cls.__annotations__.get(name)
                if annt is not None:
                    return annt

    @classmethod
    def check_meta_extra(mcs, meta: Type, errors: List):
        tags = getattr(meta, 'tags', None)
        if not tags:
            errors.append('`tags` is required')
        else:
            if not isinstance(tags, List):
                errors.append('`tags` variable has incorrect type, '
                              'should be list')
            else:
                if any([not isinstance(item, str) for item in tags]):
                    errors.append('`tags` item has incorrect type, '
                                  'should be str')

        meta_errors = getattr(meta, 'errors', [])
        if meta_errors:
            if not isinstance(meta_errors, List):
                errors.append('`errors` variable has incorrect type, '
                              'should be list')
            else:
                try:
                    if any([not issubclass(item, HttpError)
                            for item in meta_errors]):
                        raise TypeError
                except TypeError:
                    errors.append('`errors` item has incorrect type, '
                                  'should be subtype of HttpError')

        return errors

    @classmethod
    def check_meta(mcs, meta: Type, errors: List):
        from typing import _GenericAlias

        manual_validation = mcs.Meta.__manual_validation__
        for field_name in dir(mcs.Meta):
            if field_name.startswith('_') or field_name in manual_validation:
                continue

            field = getattr(meta, field_name, None)
            annt = mcs.get_annotation(mcs.Meta, field_name)

            if isinstance(annt, _GenericAlias) and annt.__origin__ == Union:
                # Union[..., ] type is unsupported
                required = False
                _type = annt.__args__[0]
            else:
                required = True
                _type = annt
            is_type = isinstance(_type, _GenericAlias) and \
                      _type.__origin__ == type
            if is_type:
                _type = _type.__args__[0]

            if required and field is None:
                errors.append(f'`{field_name}` is required')
                continue
            if field:
                if is_type:
                    try:
                        is_correct_type = issubclass(field, _type)
                    except TypeError:
                        is_correct_type = False
                    if not is_correct_type:
                        errors.append(f'`{field_name}` has incorrect type, '
                                      f'should be subclass of `{_type}`')
                elif not isinstance(field, _type):
                    errors.append(f'`{field_name}` has incorrect type, '
                                  f'should be `{_type}`')

        return errors
