"""Api extension initialization"""

from .crud_blueprint import CRUDBlueprint  # noqa


import importlib.metadata

__version__ = importlib.metadata.version("flask-smorest-sqla")
