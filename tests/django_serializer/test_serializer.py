import datetime

import pytest

from django_serializer.v2.exceptions import IncorrectMetaException
from django_serializer.v2.serializer import Serializer, ModelSerializer
from tests.tproj.app.models import SomeModel
from marshmallow import fields


class TestSerializer:
    def test_success(self):
        class T(Serializer):
            a = fields.Str()
            b = fields.Int()

        data = {"a": "a", "b": "1", "c": "c"}
        result = T().dump(data)
        assert result == {"a": "a", "b": 1}


class TestModelSerializerMeta:
    def _create_meta(self, fields: dict):
        try:

            class T(ModelSerializer):
                class SMeta:
                    for k, v in fields.items():
                        locals()[k] = v

        except IncorrectMetaException as e:
            return e.errors

    @pytest.mark.parametrize(
        "fields, errors",
        [
            ({}, ["`model` is required"]),
            ({"model": 1}, ["`model` has incorrect type"]),
            ({"model": SomeModel}, None),
            ({"model": SomeModel, "fields": 1}, ["`fields` has incorrect type"]),
            (
                {"model": SomeModel, "fields": {"error"}},
                ["`error` does not exist into model"],
            ),
            ({"model": SomeModel, "fields": {"i"}}, None),
            ({"model": SomeModel, "exclude": 1}, ["`exclude` has incorrect type"]),
            (
                {"model": SomeModel, "exclude": {"error"}},
                ["`error` does not exist into model"],
            ),
            ({"model": SomeModel, "exclude": {"nullable"}}, None),
        ],
    )
    def test_validation(self, fields, errors):
        res = self._create_meta(fields)
        assert res == errors


class TestModelSerializer:
    @pytest.fixture
    def model(self, freeze_t):
        return SomeModel(i=1, f=1.1, nullable=None, created=datetime.datetime.now())

    def test_success(self, model):
        class T(ModelSerializer):
            class SMeta:
                model = SomeModel

        res = T().dump(model)
        assert res == {
            "created": "2020-02-28T16:00:00",
            "f": 1.1,
            "i": 1,
            "id": None,
            "nullable": None,
        }

    def test_fields(self, model):
        class T(ModelSerializer):
            class SMeta:
                model = SomeModel
                fields = {"created"}

        res = T().dump(model)
        assert res == {"created": "2020-02-28T16:00:00"}

    def test_exclude(self, model):
        class T(ModelSerializer):
            class SMeta:
                model = SomeModel
                exclude = {"created"}

        res = T().dump(model)
        assert res == {"f": 1.1, "i": 1, "id": None, "nullable": None}
