import pytest

from tests.tproj.app.models import SomeModel


class TestCreateApiView:
    def test_bad_request(self, json_client):
        resp = json_client.post('/create')
        assert resp.status_code == 400
        document = resp.json()
        assert document == {
            'data': {},
            'field_problems': {'f': ['This field is required.'],
                               'i': ['This field is required.'],
                               'nullable': ['This field is required.']},
            'message': 'Bad request',
            'status': 'bad_request',
        }

    @pytest.mark.usefixtures('db', 'freeze_t')
    def test_success(self, json_client):
        resp = json_client.post('/create', json={
            'f': 1.1,
            'i': 1,
            'nullable': 'null'
        })
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            'data': {
                'created': '2020-02-28T16:00:00+00:00',
                'f': 1.1,
                'i': 1,
                'id': 1,
                'nullable': 'null'
            },
            'status': 'ok',
        }


class TestGetApiView:
    def test_bad_request(self, client):
        resp = client.get('/get_model')
        assert resp.status_code == 400
        document = resp.json()
        assert document == {
            'data': {},
            'field_problems': {'id': ['This field is required.']},
            'message': 'Bad request',
            'status': 'bad_request',
        }

    @pytest.mark.usefixtures('db')
    def test_404(self, client):
        resp = client.get('/get_model', {'id': 1})
        assert resp.status_code == 404
        document = resp.json()
        assert document == {
            'data': {},
            'message': 'Not Found',
            'status': 'not_found'
        }

    def test_without_perm(self, client, some_model_without_perm):
        resp = client.get('/get_model', {'id': some_model_without_perm.pk})
        assert resp.status_code == 403
        document = resp.json()
        assert document == {
            'data': {},
            'message': 'Forbidden',
            'status': 'forbidden'
        }

    def test_success(self, client, some_model):
        resp = client.get('/get_model', {'id': some_model.pk})
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            'data': {
                'created': '2020-02-28T16:00:00+00:00',
                'f': 1.0,
                'i': 1,
                'id': 1,
                'nullable': None
            },
            'status': 'ok',
        }


class TestUpdateApiView:
    def test_bad_request(self, json_client):
        resp = json_client.post('/update', json={})
        assert resp.status_code == 400
        document = resp.json()
        assert document == {
            'data': {},
            'field_problems': {'id': ['This field is required.']},
            'message': 'Bad request',
            'status': 'bad_request',
        }

    @pytest.mark.usefixtures('db')
    def test_404(self, json_client):
        resp = json_client.post('/update', json={'id': 1})
        assert resp.status_code == 404
        document = resp.json()
        assert document == {
            'data': {},
            'message': 'Not Found',
            'status': 'not_found'
        }

    def test_without_perm(self, json_client, some_model_without_perm):
        resp = json_client.post('/update', json={
            'id': some_model_without_perm.pk
        })
        assert resp.status_code == 403
        document = resp.json()
        assert document == {
            'data': {},
            'message': 'Forbidden',
            'status': 'forbidden'
        }

    def test_success(self, json_client, some_model):
        resp = json_client.post('/update', json={
            'id': some_model.pk,
            'f': 2,
            'i': 2,
            'nullable': 'new'
        })
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            'data': {'created': '2020-02-28T16:00:00+00:00',
                     'f': 2.0,
                     'i': 2,
                     'id': 1,
                     'nullable': 'new'},
            'status': 'ok',
        }
        some_model = SomeModel.objects.get(pk=some_model.pk)
        assert some_model.nullable == 'new'


class TestDeleteApiView:
    def test_bad_request(self, json_client):
        resp = json_client.post('/delete', json={})
        assert resp.status_code == 400
        document = resp.json()
        assert document == {
            'data': {},
            'field_problems': {'id': ['This field is required.']},
            'message': 'Bad request',
            'status': 'bad_request',
        }

    @pytest.mark.usefixtures('db')
    def test_404(self, json_client):
        resp = json_client.post('/delete', json={'id': 1})
        assert resp.status_code == 404
        document = resp.json()
        assert document == {
            'data': {},
            'message': 'Not Found',
            'status': 'not_found'
        }

    def test_without_perm(self, json_client, some_model_without_perm):
        resp = json_client.post('/delete', json={
            'id': some_model_without_perm.pk
        })
        assert resp.status_code == 403
        document = resp.json()
        assert document == {
            'data': {},
            'message': 'Forbidden',
            'status': 'forbidden'
        }

    def test_success(self, json_client, some_model):
        resp = json_client.post('/delete', json={
            'id': some_model.pk,
        })
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            'data': {},
            'status': 'ok',
        }
        assert not SomeModel.objects.filter(pk=some_model.pk).exists()


class TestListApiView:
    @pytest.mark.usefixtures('some_model')
    def test_simple(self, client):
        resp = client.get('/list')
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            'data': [{
                'created': '2020-02-28T16:00:00+00:00',
                'f': 1.0,
                'i': 1,
                'id': 1,
                'nullable': None
            }],
            'status': 'ok',
        }

    def test_paginate(self, client, some_model, some_model_without_perm):
        resp = client.get('/paginate_list', {'from_id': some_model.id})
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            'data': {'count': 2,
                     'list': [{'created': '2020-02-28T16:00:00+00:00',
                               'f': 1.0,
                               'i': 1,
                               'id': 2,
                               'nullable': 'without_permissions'}]},
            'status': 'ok',
        }

    @pytest.mark.parametrize(
        "search_query, index",
        [
            ({"limit": 2}, 0),
            ({"offset": 2}, 1),
            ({"limit": 2, "offset": 2}, 2),
            ({"all": True}, 3),
        ],
    )
    def test_limit_offset_paginate(
        self,
        client,
        some_model,
        some_model_2,
        some_model_3,
        some_model_without_perm,
        search_query,
        index,
    ):
        entities = (
            (some_model, some_model_2),
            (some_model_3, some_model_without_perm),
            (some_model_3, some_model_without_perm),
            (
                some_model,
                some_model_2,
                some_model_3,
                some_model_without_perm,
            ),
        )

        resp = client.get("/limit_offset_paginate_list", search_query)
        assert resp.status_code == 200
        document = resp.json()
        assert document == {
            "data": [
                {
                    "created": i.created.isoformat(),
                    "f": i.f,
                    "i": i.i,
                    "id": i.id,
                    "nullable": i.nullable,
                }
                for i in entities[index]
            ],
            "status": "ok",
        }
