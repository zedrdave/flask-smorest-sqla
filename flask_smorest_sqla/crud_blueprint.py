"""Subclass of flask-smorest Blueprint that registers default CRUD routes for a given SQLAlchemy model."""

from http import HTTPStatus
from importlib import import_module

import marshmallow as ma
import sqlalchemy as sqla
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.inspection import inspect

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .utils import convert_snake_to_camel


class CRUDBlueprint(Blueprint):
    """CRUD Blueprint

    Subclass of flask-smorest Blueprint that registers default CRUD routes for a given SQLAlchemy model.

    :param str name: Blueprint name
    :param str import_name: Blueprint import name
    :param db: SQLAlchemy database instance
    :param model_class: SQLAlchemy model class, or model class name if model_import_name is provided
    :param str model_import_name: Import name for SQLAlchemy model class
    :param schema_class: Marshmallow schema class, or schema class name if schema_import_name is provided
    :param str schema_import_name: Import name for Marshmallow schema class
    :param str res_id: Name of resource ID parameter in URL
    :param list methods: List of CRUD methods to register
    :param list skip_methods: List of CRUD methods to skip
    :param str update_schema: Name of Marshmallow schema class to use for PUT requests
    """

    def __init__(self, name, import_name, db, model_class, *pargs, **kwargs):  # noqa
        """Use Model and Schema arguments to register default routes."""

        if "model_import_name" not in kwargs:
            ModelCls = model_class
            model_name = ModelCls.__name__.replace("Model", "")
        else:
            model_name = convert_snake_to_camel(model_class)
            model_import_name = kwargs.pop("model_import_name",
                                           ".".join(import_name.split(".")[:-1] + ["models"]))
            ModelCls = getattr(import_module(model_import_name), model_name)
            ModelCls.__name__ = model_name

        if "schema_class" in kwargs:
            if "schema_import_name" not in kwargs:
                SchemaCls = kwargs.pop("schema_class")
            else:
                schema_name = kwargs.pop("schema_class")
                schema_import_name = kwargs.pop("schema_import_name",
                                                ".".join(import_name.split(".")[:-1] + ["schemas"]))
                SchemaCls = getattr(import_module(
                    schema_import_name), schema_name)
        else:
            # Set primary keys as dump_only:
            class SchemaPrimaryKeys:
                pass
            for col in inspect(ModelCls).primary_key:
                setattr(SchemaPrimaryKeys, col.name, ma.fields.Integer(dump_only=True))

            class SchemaCls(SQLAlchemyAutoSchema, SchemaPrimaryKeys):
                class Meta:
                    model = ModelCls
                    include_relationships = True
                    load_instance = False

            SchemaCls.__name__ = f"{model_name}Schema"

        methods = kwargs.pop(
            "methods", ["INDEX", "GET", "POST", "PUT", "DELETE"])
        skip_methods = kwargs.pop("skip_methods", [])
        methods = [m for m in methods if m not in skip_methods]

        if "PUT" in methods:
            update_schema_name = kwargs.pop("update_schema", None)
            if update_schema_name is not None:
                UpdateSchemaClsOrInst = getattr(
                    import_module(name), update_schema_name)
            else:
                UpdateSchemaClsOrInst = SchemaCls

        res_id_name = kwargs.pop("res_id", "id")

        super().__init__(name, import_name, *pargs, **kwargs)

        self_bp = self

        if "INDEX" in methods or "POST" in methods:
            @self_bp.route("/")
            class GenericIndex(MethodView):
                """
                Index endpoint.
                """

                if "INDEX" in methods:
                    @self_bp.response(HTTPStatus.OK, SchemaCls(many=True))
                    def get(self, **kwargs):
                        """List resources."""
                        return ModelCls.query.all(**kwargs)

                if "POST" in methods:
                    @self_bp.arguments(SchemaCls)
                    @self_bp.response(HTTPStatus.OK, SchemaCls)
                    @self_bp.doc(responses={
                        HTTPStatus.NOT_FOUND: {"description": f"{name} resource not found"},
                        HTTPStatus.CONFLICT: {"description": f"DB error."}
                    })
                    def post(self, new_object):
                        """Create and return new resource."""
                        try:
                            new_object = ModelCls(**new_object)
                            db.session.add(new_object)
                            db.session.commit()
                        except sqla.exc.IntegrityError as e:
                            print("Exception:", e)
                            # TODO: can probably reuse DB session from object
                            db.session.rollback()
                            abort(HTTPStatus.CONFLICT,
                                  message=f"DB error while inserting {name} resource: {e}",
                                  exc=e)
                        return new_object

        @self_bp.route(f"/<int:{res_id_name}>")
        class GenericCRUD(MethodView):
            """Resource-specific endpoints."""

            def get_or_404(self, **kwargs):
                res = ModelCls.query.filter_by(**kwargs).first()
                if res is None:
                    abort(HTTPStatus.NOT_FOUND,
                          message=f"{name} resource {kwargs} not found")
                return res

            if "GET" in methods:
                @self_bp.doc(responses={HTTPStatus.NOT_FOUND: {"description": f"{name} resource not found"}})
                @self_bp.response(HTTPStatus.OK, SchemaCls)
                def get(self, **kwargs):
                    """Fetch resource by ID."""
                    res = self.get_or_404(**kwargs)
                    return res

            if "PUT" in methods:
                @self_bp.arguments(UpdateSchemaClsOrInst)
                @self_bp.doc(
                    responses={
                        HTTPStatus.NOT_FOUND: {"description": f"{name} resource not found"},
                        HTTPStatus.CONFLICT: {"description": f"DB error."}
                    }
                )
                @self_bp.response(HTTPStatus.OK, SchemaCls)
                def put(self, payload, **kwargs):
                    """Update resource by ID."""
                    res = self.get_or_404(**kwargs)
                    try:
                        for attr, value in payload.items():
                            setattr(res, attr, value)
                        db.session.add(res)
                        db.session.commit()
                    except sqla.exc.IntegrityError as e:
                        abort(HTTPStatus.CONFLICT,
                              message=f"DB error while updating {name} resource.",
                              exc=e)
                    return res

            if "DELETE" in methods:
                @self_bp.response(HTTPStatus.NO_CONTENT, description="Resource deleted")
                # TODO: choose whether to return NO_CONTENT or list of remaining resources
                # @self_bp.response(HTTPStatus.OK, SchemaCls(many=True))
                def delete(self, **kwargs):
                    """Delete resource."""
                    res = self.get_or_404(**kwargs)
                    db.session.delete(res)
                    db.session.commit()
                    return "", HTTPStatus.NO_CONTENT
