=======================
flask-smorest-sqla
=======================

Flask REST API without the cruft
==================================

This packages builds upon `flask-smorest <https://github.com/marshmallow-code/flask-smorest>`_ and SQLAlchemy, to provide ORM integration and a boilerplate-free REST implementation with:

- CRUD endpoints
- [To do] Access Authorisation
- [To do] Authentication

Install
============

::

    pip install flask-smorest-sql


Quickstart
============

With a Flask-Smorest `api` object registered:

::

    class Test(db.Model):
        """Test model."""
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(128))

    with app.app_context():
        db.create_all()

    bp = CRUDBlueprint("Test", __name__, db=db, url_prefix="/test", model_class=TestModel)
    api.register_blueprint(bp)


Will create all CRUD endpoints for resource `Test` at URL `/test`.


Documentation
=============

Full documentation is available at http://flask-smorest-sqla.readthedocs.io/.


License
============

MIT licensed. See the `LICENSE <https://github.com/marshmallow-code/flask-smorest/blob/master/LICENSE>`_ file for more details.
