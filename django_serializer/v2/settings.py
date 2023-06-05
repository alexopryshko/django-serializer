from django.conf import settings as django_settings
from django.db import models
from marshmallow import fields as mmfields
from django_serializer.v2.parsers import JsonParser
from django_serializer.v2.renderers import JsonRenderer
from django_serializer.v2.serializer_fields import FileField


__all__ = ("settings",)


class ApiSettings:
    """
    Proxy class for django settings.
    """

    SERIALIZER_DEFAULT_PARSER_CLASS: JsonParser
    SERIALIZER_DEFAULT_RENDERER_CLASS: JsonRenderer
    DEFAULTS = {
        "SERIALIZER_DEFAULT_PARSER_CLASS": JsonParser,
        "SERIALIZER_DEFAULT_RENDERER_CLASS": JsonRenderer,
        "SERIALIZER_FIELD_MAPPING": {
            models.AutoField: mmfields.Int,
            models.BigAutoField: mmfields.Int,
            models.BooleanField: mmfields.Bool,
            models.SlugField: mmfields.Str,
            models.CharField: mmfields.Str,
            models.CommaSeparatedIntegerField: mmfields.Str,
            models.DateField: mmfields.Date,
            models.DateTimeField: mmfields.DateTime,
            models.TimeField: mmfields.Time,
            models.DurationField: mmfields.TimeDelta,
            models.DecimalField: mmfields.Decimal,
            models.EmailField: mmfields.Str,
            models.ForeignKey: mmfields.Int,
            models.OneToOneField: mmfields.Int,
            models.FloatField: mmfields.Float,
            models.IntegerField: mmfields.Int,
            models.PositiveIntegerField: mmfields.Int,
            models.PositiveSmallIntegerField: mmfields.Int,
            models.SmallIntegerField: mmfields.Int,
            models.BigIntegerField: mmfields.Int,
            models.TextField: mmfields.Str,
            models.FileField: FileField,
            models.ImageField: FileField,
            models.URLField: mmfields.Str,
            models.UUIDField: mmfields.Str,
            models.GenericIPAddressField: mmfields.Str,
        },
    }

    def __getattr__(self, attr):
        if attr == "SERIALIZER_FIELD_MAPPING":
            fields = self.DEFAULTS[attr]
            extra_fields = getattr(django_settings, attr, None)
            if extra_fields is not None:
                fields = fields.update(extra_fields)
            return fields

        user_config = getattr(django_settings, attr, None)
        if user_config is not None:
            return user_config

        return self.DEFAULTS.get(attr)


settings = ApiSettings()
