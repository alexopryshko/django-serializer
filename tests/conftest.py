import datetime
import json

import pytest
from django.conf import settings
from freezegun import freeze_time
from pytz import UTC


def wrapper(func):
    def _inner(*args, **kwargs):
        kwargs["content_type"] = "application/json"
        if "json" in kwargs:
            kwargs["data"] = json.dumps(kwargs["json"])
        return func(*args, **kwargs)

    return _inner


class JSONClient:
    def __init__(self, client):
        self.client = client

    def __getattr__(self, item):
        func = getattr(self.client, item)

        if func not in [
            self.client.force_login,
        ]:
            return wrapper(func)
        else:
            return func


@pytest.fixture
def json_client(client):
    return JSONClient(client)


@pytest.fixture
def debug_true():
    buf = settings.DEBUG
    settings.DEBUG = True
    yield
    settings.DEBUG = buf


@pytest.fixture
def freeze_t():
    now = datetime.datetime(2020, 2, 28, 16, tzinfo=UTC)
    _freeze_time = freeze_time(now)
    _freeze_time.start()
    yield now
    _freeze_time.stop()
