from django_serializer.exceptions import SerializerFieldException


class Field:
    def __init__(self, required=True, default=None, name=None):
        self.default = default
        self.required = required
        self.name = name

    def serialize(self, **kwargs):
        if 'field_value' not in kwargs:
            if not self.required:
                serialized = self.default
            else:
                raise SerializerFieldException('Field missed or has no default value')
        else:
            serialized = kwargs['field_value']
            serialized = self.serialization_handler(serialized)

        return serialized

    def serialization_handler(self, value):
        pass


class IntegerField(Field):
    def serialization_handler(self, value):
        return int(value) if value is not None else None


class BooleanField(Field):
    def serialization_handler(self, value):
        return int(value) if value is not None else None


class CharField(Field):
    def serialization_handler(self, value):
        return str(value) if value is not None else None


class DateField(Field):
    def serialization_handler(self, value):
        from django.utils.dateformat import format
        return format(value, 'U') if value is not None else None


class DateTimeField(Field):
    def serialization_handler(self, value):
        from django.utils.dateformat import format
        return format(value, 'U') if value is not None else None


class TimeField(Field):
    def serialization_handler(self, value):
        return str(value) if value is not None else None


class FloatField(Field):
    def serialization_handler(self, value):
        return float(value) if value is not None else None


class ModelField(Field):
    def serialization_handler(self, value):
        return value if value is not None else None


# class PointField(Field):
#     def serialization_handler(self, value):
#         if value is not None:
#             return {
#                 'lng': value.x,
#                 'lat': value.y
#             }


# class JSONField(Field):
#     def serialization_handler(self, value):
#         if value is not None:
#             return dict(value)


# class ArrayField(Field):
#     def serialization_handler(self, value):
#         if value is not None:
#             return list(value)


class ImageField(Field):
    def serialization_handler(self, value):
        if value:
            try:
                return value.url
            except ValueError:
                return None


class SerializerField(Field):
    def __init__(self, **kwargs):
        source = kwargs.pop('source')
        self.source = source
        self.serializer = None
        super().__init__(**kwargs)

    def serialization_handler(self, obj):
        if callable(self.source):
            return self.source(obj)
        return getattr(self.serializer, self.source)(obj)
