# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""

import re


def convert_snake_to_camel(word):
    """🐍 → 🐪."""
    return "".join(x.capitalize() or "_" for x in word.split("_"))


def convert_camel_to_snake(word):
    """🐪 → 🐍."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', word)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
