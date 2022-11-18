from django import forms
from django.conf import settings
from django.forms import ModelForm
from marshmallow import Schema, fields

from django_serializer.v2.exceptions import HttpError, \
    IncorrectSettingsException


class IntList(fields.List):
    def __init__(self, *args, **kwargs):
        super().__init__(fields.Integer, *args, **kwargs)


class StrList(fields.List):
    def __init__(self, *args, **kwargs):
        super().__init__(fields.String, *args, **kwargs)


FORM_FIELD_MAPPING = {
    forms.IntegerField: fields.Int,
    forms.BooleanField: fields.Bool,
    forms.CharField: fields.Str,
    forms.DateField: fields.Date,
    forms.DateTimeField: fields.DateTime,
    forms.TimeField: fields.Time,
    forms.DecimalField: fields.Decimal,
    forms.EmailField: fields.Email,
    forms.FloatField: fields.Float,
    # forms.ImageField: ImageField,
    forms.URLField: fields.Url,
    forms.ModelMultipleChoiceField: IntList,
    forms.MultipleChoiceField: StrList,
    forms.ModelChoiceField: fields.Int,
    forms.TypedChoiceField: fields.Str,
}

extra_fields = getattr(
    settings, 'SERIALIZER_FORM_FIELD_MAPPING', None
)
if extra_fields:
    if not isinstance(extra_fields, dict):
        raise IncorrectSettingsException(
            '`SERIALIZER_FORM_FIELD_MAPPING` has incorrect type'
        )
    FORM_FIELD_MAPPING.update(extra_fields)


def form2schema(field: forms.Form) -> Schema:
    if field is None:
        return None

    if issubclass(field, ModelForm):
        form_fields = field().base_fields
    else:
        form_fields = field.declared_fields

    schema_fields = {}
    for name, field in form_fields.items():
        schema_fields.update(
            {name: FORM_FIELD_MAPPING[type(field)](required=field.required)})
    schema = Schema.from_dict(schema_fields)
    return schema


def generate_error_schema(swagger, error: HttpError) -> Schema:
    key = ''.join([str(error.http_code), error.alias])
    if swagger.error_classes.get(key) is not None:
        return swagger.error_classes[key]
    schema_fields = dict(status=fields.String(example=error.alias),
                         message=fields.String(example=error.description),
                         data=fields.Dict())
    if getattr(error, 'field_problems', None) is not None:
        schema_fields.update({'fields_problems': fields.Dict()})

    schema = Schema.from_dict(
        schema_fields,
        name=''.join([i.capitalize() for i in error.description.split()])
    )
    swagger.error_classes[key] = schema
    return schema


def merge_schemas(first_schema: Schema, second_schema: Schema) -> Schema:
    if first_schema is None and second_schema is None:
        return None
    elif first_schema is None or second_schema is None:
        return first_schema or second_schema

    common_fields = {}
    for k, v in first_schema._declared_fields.items():
        common_fields[k] = v
    for k, v in second_schema._declared_fields.items():
        common_fields[k] = v
    schema = Schema.from_dict(common_fields)
    return schema
