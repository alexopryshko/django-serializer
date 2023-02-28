import pytest

from tests.tproj.app.models import SomeModel


@pytest.fixture
def some_model(db, freeze_t):
    return SomeModel.objects.create(i=1, f=1, nullable=None)


@pytest.fixture
def some_model_2(db, freeze_t):
    return SomeModel.objects.create(i=2, f=2, nullable="test")


@pytest.fixture
def some_model_3(db, freeze_t):
    return SomeModel.objects.create(i=3, f=3, nullable="another_test")


@pytest.fixture
def some_model_without_perm(db, freeze_t):
    return SomeModel.objects.create(i=1, f=1, nullable='without_permissions')
