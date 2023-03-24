"""Test Blueprint extra features"""

import pytest

from http import HTTPStatus
import json
import marshmallow as ma
from flask.views import MethodView

from flask_smorest_sqla import CRUDBlueprint


class TestBlueprint:
    """Test Blueprint class"""

    @pytest.mark.parametrize("openapi_version", ("2.0", "3.0.2"))
    def test_crud_blueprint(self, app, api, db, client, openapi_version):
        """
        Check blueprint registration and CRUD operations
        """

        class TestModel(db.Model):
            """Test model."""
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(128))

        with app.app_context():
            db.create_all()

        bp = CRUDBlueprint("test", __name__, db=db, url_prefix="/test", model_class=TestModel)
        api.register_blueprint(bp)

        spec = api.spec.to_dict()
        # Check tags are correctly set and docs only differ by tags
        if openapi_version == "3.0.2":
            assert "Test" in spec["components"]["schemas"]
        assert "/test/" in spec["paths"]
        for method in ("get", "post"):
            assert method in spec["paths"]["/test/"]
        assert "/test/{id}" in spec["paths"]
        for method in ("get", "put", "delete"):
            assert method in spec["paths"]["/test/{id}"]

        # Test CRUD operations through the API:
        headers = {"Content-type": "application/json"}

        res = client.open(
            path="/test/",
            method="GET",
            headers=headers,
        )
        assert res.status_code == HTTPStatus.OK
        assert res.json == []

        RES_NAME = "foobar"
        res = client.open(
            path="/test/",
            method="POST",
            headers=headers,
            data=json.dumps({"name": RES_NAME})
        )
        assert res.status_code == HTTPStatus.OK
        for key in ("id", "name"):
            assert key in res.json
        insert_id = res.json["id"]

        res = client.open(
            path=f"/test/{insert_id}",
            method="GET",
            headers=headers,
        )
        assert res.status_code == HTTPStatus.OK
        assert res.json["id"] == insert_id
        assert res.json["name"] == RES_NAME

        RES_NEW_NAME = "barfoo"
        res = client.open(
            path=f"/test/{insert_id}",
            method="PUT",
            headers=headers,
            data=json.dumps({"name": RES_NEW_NAME})
        )
        assert res.status_code == HTTPStatus.OK
        assert res.json["id"] == insert_id
        assert res.json["name"] == RES_NEW_NAME

        res = client.open(
            path=f"/test/{insert_id}",
            method="GET",
            headers=headers,
        )
        assert res.status_code == HTTPStatus.OK
        assert res.json["id"] == insert_id
        assert res.json["name"] == RES_NEW_NAME

        res = client.open(
            path="/test/",
            method="GET",
            headers=headers,
        )
        assert res.status_code == HTTPStatus.OK
        assert len(res.json) == 1

        res = client.open(
            path=f"/test/{insert_id}",
            method="DELETE",
            headers=headers,
        )
        assert res.status_code == HTTPStatus.NO_CONTENT

        res = client.open(
            path="/test/",
            method="GET",
            headers=headers,
        )
        assert res.status_code == HTTPStatus.OK
        assert len(res.json) == 0
