.. _quickstart:
.. currentmodule:: flask_smorest

Quickstart
==========

With a Flask-Smorest `api` object registered:

::

    class Test(db.Model):
        """Test model."""
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(128))

    with app.app_context():
        db.create_all()

    bp = CRUDBlueprint("test", __name__, db=db, url_prefix="/test", model_class=TestModel)
    api.register_blueprint(bp)


Will create all CRUD endpoints for resource `Test` at endpoint `/test`.
