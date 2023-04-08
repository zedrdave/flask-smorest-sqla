"""Api extension initialization"""

from .crud_blueprint import CRUDBlueprint  # noqa

import re
import os

with open(os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")) as f:
    version = re.search(r'version = "(.*)"', f.read()).group(1)

__version__ = version
