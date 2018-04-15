from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.base import ModelBase

from django_serializer.exceptions import MissEntityTypeException, DuplicateEntityTypeException


ENTITY_TYPE_LENGTH = 16
ENTITY_ID_LENGTH = 64 - ENTITY_TYPE_LENGTH
_ENTITY_TYPE_MAX_VALUE = int('1' * ENTITY_TYPE_LENGTH, 2)
_ENTITY_ID_MAX_VALUE = int('1' * ENTITY_ID_LENGTH, 2)
_ENTITY_TYPE_MASK = _ENTITY_TYPE_MAX_VALUE << ENTITY_ID_LENGTH
_ENTITY_ID_MASK = ~_ENTITY_TYPE_MASK


class EntityMixinMeta(ModelBase):
    entity_types = {}

    def __new__(mcs, name, bases, attrs):
        if 'EntityMixin' == name or 'ENTITY_TYPE' not in attrs:
            new = super(EntityMixinMeta, mcs).__new__(mcs, name, bases, attrs)
            return new

        entity_type = attrs['ENTITY_TYPE']
        if entity_type is None:
            raise MissEntityTypeException('You have missed entity_type in {}'.format(name))

        if entity_type in mcs.entity_types:
            raise DuplicateEntityTypeException(
                'Model({}) with the same entity type already exist'.format(mcs.entity_types[entity_type].__name__)
            )

        attrs['entity_types'] = mcs.entity_types

        new = super(EntityMixinMeta, mcs).__new__(mcs, name, bases, attrs)
        mcs.entity_types[entity_type] = new

        return new

    def check_entity_type(cls, entity_type):
        return entity_type in cls.entity_types


class EntityMixin(metaclass=EntityMixinMeta):
    ENTITY_TYPE = None

    def get_entity_id(self):
        entity_type = int(self.ENTITY_TYPE)
        entity_id = int(self.pk)

        object_id = entity_type << ENTITY_ID_LENGTH
        object_id |= entity_id
        return object_id

    def get_entity_by_id(self, entity_id):
        if not entity_id:
            return
        entity_type, entity_id = split_object_id(entity_id)
        return self.entity_types[entity_type].objects.get(pk=entity_id)


class EntityField(models.BigIntegerField):
    @staticmethod
    def validate_object_id(value):
        if not check_object_id(value):
            raise ValidationError('%(value)s is not valid object id', params={'value': value})

    def __init__(self, *args, **kwargs):
        self.available_entities = kwargs.pop('available_entities', [])
        kwargs.update({
            'db_index': True,
            'validators': [self.validate_object_id]
        })
        super().__init__(*args, **kwargs)


def split_object_id(object_id):
    object_id = int(object_id)
    entity_type = (object_id & _ENTITY_TYPE_MASK) >> ENTITY_ID_LENGTH
    entity_id = object_id & _ENTITY_ID_MASK
    return entity_type, entity_id


def check_object_id(object_id, entity_type=None):
    try:
        object_id = int(object_id)
    except ValueError as e:
        return False

    object_entity_type, entity_id = split_object_id(object_id)

    if not EntityMixin.check_entity_type(object_entity_type):
        return False

    if entity_type and object_entity_type != entity_type:
        return False

    return True
