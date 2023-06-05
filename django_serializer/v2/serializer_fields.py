import typing

from marshmallow import fields

__all__ = ("FileField",)


class FileField(fields.Str):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is not None:
            value = value.url
        return super()._serialize(value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        raise NotImplementedError
