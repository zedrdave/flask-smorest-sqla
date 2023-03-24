import pytest

import marshmallow as ma

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api


class AppConfig:
    """Base application configuration class

    Overload this to add config parameters
    """

    API_TITLE = "API Test"
    API_VERSION = "1"
    OPENAPI_VERSION = "3.0.2"
    TESTING = True
    # Use in-memory SQLite database:
    SQLALCHEMY_DATABASE_URI = "sqlite:///"


@pytest.fixture(params=[AppConfig])
def app(request):
    _app = Flask(__name__)
    _app.config.from_object(request.param)
    return _app


@pytest.fixture()
def db(app):
    db = SQLAlchemy()
    db.init_app(app)
    return db


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def api(app):
    return Api(app)
