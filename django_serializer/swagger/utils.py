from django import forms
from django.forms import ModelForm, modelform_factory
from marshmallow import Schema, fields

from django_serializer.v2.exceptions import HttpError

FORM_FIELD_MAPPING = {
    forms.IntegerField: fields.Int,
    forms.BooleanField: fields.Bool,
    forms.CharField: fields.Str,
    forms.DateField: fields.Date,
    forms.DateTimeField: fields.DateTime,
    forms.TimeField: fields.Time,
    forms.DecimalField: fields.Decimal,
    forms.EmailField: fields.Str,
    forms.FloatField: fields.Float,
    # forms.ImageField: ImageField,
    forms.URLField: fields.Str
}


def form2schema(form: forms.Form) -> Schema:
    if form is None:
        return None

    if issubclass(form, ModelForm):
        # ModelForm по умолчанию не инициализирована, поэтому надо применить
        # modelform_factory, чтобы получить поля
        form = modelform_factory(form.model, fields=form.fields)
        form_fields = form.base_fields
    else:
        form_fields = form.declared_fields

    schema = schema_factory(str(id(form)), form_fields.keys())

    schema_fields = {}
    for name, form in form_fields.items():
        schema_fields.update(
            {name: FORM_FIELD_MAPPING[type(form)](required=form.required)})
    schema = schema(**schema_fields)
    return schema


def schema_factory(name, arg_names, base_class=Schema):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in arg_names:
                raise TypeError("Argument %s is not valid for %s"
                                % (key, self.__class__.__name__))
            self._declared_fields[key] = value
        base_class.__init__(self)

    new_class = type(name, (base_class,), {"__init__": __init__})
    return new_class


def _generate_error_schema(swagger, error: HttpError) -> Schema:
    key = ''.join([str(error.http_code), error.alias, error.description])
    try:
        schema = swagger.error_classes[key]
    except KeyError:
        schema = schema_factory(
            ''.join([i.capitalize() for i in error.description.split()]),
            ['status', 'message', 'data'])
        schema = schema(
            status=fields.String(example=error.alias),
            message=fields.String(example=error.description),
            data=fields.Dict(),
        )
        swagger.error_classes[key] = schema
    return schema


def _merge_schemas(body_schema: Schema, model_schema: Schema) -> Schema:
    if body_schema is None and model_schema is None:
        return None
    elif body_schema is None or model_schema is None:
        return body_schema or model_schema

    common_fields = {}
    for k, v in body_schema.declared_fields.items():
        common_fields[k] = v
    for k, v in model_schema.declared_fields.items():
        common_fields[k] = v
    schema = schema_factory('body_form_schema', common_fields.keys())
    schema(**common_fields)
    return schema
