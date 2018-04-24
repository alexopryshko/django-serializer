from django.conf import settings
from django.db import models

from django_serializer.model.base import EntityField
from django_serializer.exceptions import MetaSerializerException, MappingSerializerException
from django_serializer.serializer.fields import (
    Field,
    IntegerField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ModelField,
    SerializerField,
    TimeField,
    ImageField,
)

SERIALIZER_FIELD_MAPPING = {
    models.AutoField: IntegerField,
    models.BigIntegerField: IntegerField,
    models.BooleanField: BooleanField,
    models.CharField: CharField,
    models.CommaSeparatedIntegerField: CharField,
    models.DateField: DateField,
    models.DateTimeField: DateTimeField,
    models.TimeField: TimeField,
    models.DecimalField: IntegerField,
    models.EmailField: CharField,
    models.ForeignKey: ModelField,
    models.OneToOneField: ModelField,
    models.FloatField: FloatField,
    models.IntegerField: IntegerField,
    models.PositiveIntegerField: IntegerField,
    models.PositiveSmallIntegerField: IntegerField,
    models.SmallIntegerField: IntegerField,
    models.TextField: CharField,
    EntityField: IntegerField,
    models.ImageField: ImageField,
    models.URLField: CharField
}
EXTRA_SERIALIZER_FIELD_MAPPING = getattr(
    settings, 'SERIALIZER_FIELD_MAPPING', None
)
if EXTRA_SERIALIZER_FIELD_MAPPING:
    assert isinstance(EXTRA_SERIALIZER_FIELD_MAPPING, dict), \
        'SERIALIZER_FIELD_MAPPING should be dict'
    SERIALIZER_FIELD_MAPPING.update(EXTRA_SERIALIZER_FIELD_MAPPING)


class SerializerMeta(type):
    def __new__(mcs, name, bases, attrs):
        serializer_attrs = attrs.copy()

        for base_class in bases:
            serializer_attrs.update(base_class.__dict__)
            for c in reversed(base_class.__mro__):
                serializer_attrs.update(c.__dict__)

        attrs['serializer_attrs'] = []

        for field_name, field in serializer_attrs.items():
            if isinstance(field, Field):
                attrs['serializer_attrs'].append((field_name, field))

        new = super(SerializerMeta, mcs).__new__(mcs, name, bases, attrs)
        return new


class Serializer(metaclass=SerializerMeta):
    def __init__(self, obj, multiple=False, dict_format=False, dict_key='id'):
        self.obj = obj
        self.multiple = multiple
        self.dict_format = dict_format
        self.dict_key = dict_key

    def _get_fields(self):
        return getattr(self, 'serializer_attrs')

    def _get_extractor(self, obj):
        def obj_extractor(inner_obj, field):
            try:
                return getattr(inner_obj, field)
            except AttributeError:
                return getattr(self, field)(inner_obj)

        def dict_extractor(inner_obj, field):
            try:
                return inner_obj[field]
            except KeyError:
                return getattr(self, field)(inner_obj)

        if isinstance(obj, dict):
            return dict_extractor
        else:
            return obj_extractor

    def _serialize_obj(self, obj):
        serialized = {}

        fields = self._get_fields()
        extractor = self._get_extractor(obj)

        for field_name, field in fields:
            try:
                if isinstance(field, SerializerField):
                    field.serializer = self
                    serialized_field_value = field.serialize(field_value=obj)
                else:
                    obj_field_value = extractor(obj, field_name)
                    serialized_field_value = field.serialize(field_value=obj_field_value)
            except AttributeError:
                serialized_field_value = field.serialize()
            serialized[field_name] = serialized_field_value

        return serialized

    def serialize(self):
        if self.obj is None:
            return None

        if self.multiple:
            if self.dict_format:
                result = {}
                for obj_item in self.obj:
                    result[getattr(obj_item, self.dict_key)] = self._serialize_obj(obj_item)
            else:
                result = []
                for obj_item in self.obj:
                    result.append(self._serialize_obj(obj_item))
        else:
            if self.dict_format:
                result = {getattr(self.obj, self.dict_key): self._serialize_obj(self.obj)}
            else:
                result = self._serialize_obj(self.obj)

        return result


class ModelSerializerMeta(SerializerMeta):
    def __new__(mcs, name, bases, attrs):
        if name == 'ModelSerializer':
            new = super(ModelSerializerMeta, mcs).__new__(mcs, name, bases, attrs)
            return new

        Meta = None
        try:
            Meta = attrs['Meta']
        except KeyError:
            for base in bases:
                if 'Meta' in base.__dict__:
                    Meta = base.__dict__['Meta']
                    break
                for c in reversed(base.__mro__):
                    if 'Meta' in c.__dict__:
                        Meta = c.__dict__['Meta']
                        break
        if not Meta:
            raise MetaSerializerException('{} serializer have not Meta'.format(name))

        try:
            model = Meta.model
        except AttributeError:
            raise MetaSerializerException('{}.Meta have not model'.format(name))

        meta_fields = getattr(Meta, 'fields', None)
        if meta_fields and not isinstance(meta_fields, (tuple, list)):
            raise MetaSerializerException('{}.Meta.fields have incorrect format'.format(name))

        meta_fields = set(meta_fields) if meta_fields else None

        meta_exclude = getattr(Meta, 'exclude', None)
        if meta_exclude and not isinstance(meta_exclude, (tuple, list)):
            raise MetaSerializerException('{}.Meta.meta_exclude have incorrect format'.format(name))

        meta_exclude = set(meta_exclude) if meta_exclude else None

        model_fields = model._meta.fields
        for model_field in model_fields:
            model_field_class = model_field.__class__

            if meta_fields is not None and model_field.attname not in meta_fields:
                continue

            if meta_exclude is not None and model_field.attname in meta_exclude:
                continue

            if hasattr(model_field_class, 'serializer'):
                serializer_field_class = model_field_class.serializer
            else:
                try:
                    serializer_field_class = SERIALIZER_FIELD_MAPPING[model_field_class]
                except KeyError:
                    raise MappingSerializerException('{} is not supported'.format(model_field_class))

            attrs[model_field.attname] = serializer_field_class()

        new = super(ModelSerializerMeta, mcs).__new__(mcs, name, bases, attrs)
        return new


class ModelSerializer(Serializer, metaclass=ModelSerializerMeta):
    pass


class MultiSerializer(Serializer):
    serializers = {}

    def get_serializer_class(self, obj, **kwargs):
        raise NotImplementedError

    def get_serializer_kwargs(self, obj, **kwargs):
        return {
            'obj': obj
        }

    def _serialize_obj(self, obj):
        serializer_class = self.get_serializer_class(obj)
        return serializer_class(**self.get_serializer_kwargs(obj)).serialize()
