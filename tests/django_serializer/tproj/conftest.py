import pytest

from tests.tproj.app.models import SomeModel


@pytest.fixture
def some_model(db, freeze_t):
    return SomeModel.objects.create(i=1, f=1, nullable=None)


@pytest.fixture
def some_model_without_perm(db, freeze_t):
    return SomeModel.objects.create(i=1, f=1, nullable='without_permissions')
