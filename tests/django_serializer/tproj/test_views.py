import pytest


class TestApiViews:
    def test_get_view(self, client):
        resp = client.get("/get")
        assert resp.status_code == 200
        document = resp.json()
        assert document == {"data": {}, "status": "ok"}

    def test_get_query_view_error(self, client):
        resp = client.get("/get_query")
        assert resp.status_code == 400
        document = resp.json()
        assert document == {
            "data": {},
            "field_problems": {"q": ["This field is required."]},
            "message": "Bad request",
            "status": "bad_request",
        }

    def test_get_query_view_success(self, client):
        resp = client.get("/get_query", {"q": 1})
        assert resp.status_code == 200
        document = resp.json()
        assert document == {"data": {"q": "1"}, "status": "ok"}

    def test_post_view(self, client):
        resp = client.get("/post")
        assert resp.status_code == 405
        document = resp.json()
        assert document == {
            "data": {},
            "message": "Not implemented",
            "status": "not_implemented",
        }

        resp = client.post("/post")
        document = resp.json()
        assert resp.status_code == 200
        assert document == {"data": {}, "status": "ok"}

    def test_post_body_view_error(self, json_client):
        resp = json_client.post("/post_body")
        assert resp.status_code == 400
        document = resp.json()
        assert document == {
            "data": {},
            "field_problems": {"q": ["This field is required."]},
            "message": "Bad request",
            "status": "bad_request",
        }

    def test_post_body_view_success(self, json_client):
        resp = json_client.post("/post_body", json={"q": 1})
        assert resp.status_code == 200
        document = resp.json()
        assert document == {"data": {"q": "1"}, "status": "ok"}

    def test_500_debug_false(self, client):
        resp = client.get("/500")
        assert resp.status_code == 500
        document = resp.json()
        assert document == {
            "data": {},
            "message": "Internal server error",
            "status": "internal_error",
        }

    @pytest.mark.usefixtures("debug_true")
    def test_500_debug_true(self, client):
        try:
            client.get("/500")
            assert False
        except ZeroDivisionError:
            assert True

    def test_serializer(self, client):
        resp = client.get("/serializer")
        assert resp.status_code == 200
        document = resp.json()
        assert document == {"data": {"a": 1}, "status": "ok"}

    def test_serializer_many(self, client):
        resp = client.get("/serializer_many")
        assert resp.status_code == 200
        document = resp.json()
        assert document == {"data": [{"a": 1}], "status": "ok"}
