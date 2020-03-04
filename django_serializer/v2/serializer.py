from typing import Type, Set

from django.conf import settings
from django.db import models
from marshmallow import Schema, fields
from marshmallow.schema import SchemaMeta

from django_serializer.v2.exceptions import (
    IncorrectMetaException,
    IncorrectSettingsException,
)

SERIALIZER_FIELD_MAPPING = {
    models.AutoField: fields.Int,
    models.BigIntegerField: fields.Int,
    models.BooleanField: fields.Bool,
    models.CharField: fields.Str,
    models.CommaSeparatedIntegerField: fields.Str,
    models.DateField: fields.Date,
    models.DateTimeField: fields.DateTime,
    models.TimeField: fields.Time,
    models.DecimalField: fields.Decimal,
    models.EmailField: fields.Str,
    models.ForeignKey: fields.Int,
    models.OneToOneField: fields.Int,
    models.FloatField: fields.Float,
    models.IntegerField: fields.Int,
    models.PositiveIntegerField: fields.Int,
    models.PositiveSmallIntegerField: fields.Int,
    models.SmallIntegerField: fields.Int,
    models.TextField: fields.Str,
    # models.ImageField: ImageField,
    models.URLField: fields.Str
}
extra_fields = getattr(
    settings, 'SERIALIZER_FIELD_MAPPING', None
)
if extra_fields:
    if not isinstance(extra_fields, dict):
        raise IncorrectSettingsException(
            '`SERIALIZER_FIELD_MAPPING` has incorrect type'
        )
    SERIALIZER_FIELD_MAPPING.update(extra_fields)


class Serializer(Schema):
    pass


class ModelSerializerMeta(SchemaMeta):
    @staticmethod
    def check_fields(name: str,
                     fields_name: str,
                     meta: Type,
                     model_fields_set: Set):
        meta_fields = getattr(meta, fields_name, None)
        if meta_fields and not isinstance(meta_fields, (tuple, list, set)):
            raise IncorrectMetaException(
                name, [f'`{fields_name}` has incorrect type']
            )
        if meta_fields:
            errors = []
            for item in list(meta_fields):
                if item not in model_fields_set:
                    errors.append(f'`{item}` does not exist into model')
            if errors:
                raise IncorrectMetaException(name, errors)
            return set(meta_fields)

    def __new__(mcs, name, bases, attrs, *args, **kwargs):
        if name == 'ModelSerializer':
            # noinspection PyArgumentList
            new = super().__new__(mcs, name, bases, attrs, *args, **kwargs)
            return new

        meta = None
        try:
            meta = attrs['SMeta']
        except KeyError:
            for base in bases:
                meta = getattr(base, 'SMeta', None)
                if meta:
                    break
        if not meta:
            raise IncorrectMetaException(
                name, ['serializer have not `SMeta` class']
            )

        model: Type[models.Model] = getattr(meta, 'model', None)
        if not model:
            raise IncorrectMetaException(name, ['`model` is required'])

        try:
            if not issubclass(model, models.Model):
                raise TypeError
        except TypeError:
            raise IncorrectMetaException(name, ['`model` has incorrect type'])
        model_fields_set = {f.attname for f in model._meta.fields}
        model_fields = model._meta.fields

        meta_fields = mcs.check_fields(name, 'fields', meta, model_fields_set)
        meta_exclude = mcs.check_fields(name, 'exclude', meta, model_fields_set)
        if meta_fields and meta_exclude:
            raise IncorrectMetaException(name, ['`fields` and `exclude` '
                                                'can not be simultaneously '])

        errors = []
        for model_field in model_fields:
            model_field_class = model_field.__class__
            if meta_fields and model_field.attname not in meta_fields:
                continue
            if meta_exclude and model_field.attname in meta_exclude:
                continue
            try:
                field_class = SERIALIZER_FIELD_MAPPING[model_field_class]
                attrs[model_field.attname] = field_class()
            except KeyError:
                errors.append(
                    f'`{model_field.attname}` has unknown type '
                    f'{model_field_class}, you should add rule to '
                    f'SERIALIZER_FIELD_MAPPING in django settings'
                )
        if errors:
            raise IncorrectMetaException(name, errors)

        return super(ModelSerializerMeta, mcs).__new__(mcs, name, bases, attrs)


class ModelSerializer(Serializer, metaclass=ModelSerializerMeta):
    pass
