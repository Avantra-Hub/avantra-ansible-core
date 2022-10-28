# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import re

_pattern_first = re.compile('(.)([A-Z][a-z]+)')
_pattern_second = re.compile('__([A-Z])')
_pattern_third = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake_case(camel: str = ""):
    """
    Converts a camel case string to snake case.
    :param camel: the camel case string
    :return: the corresponding snake case string
    """
    if camel is None:
        return None
    name = re.sub(_pattern_first, r'\1_\2', camel)
    name = re.sub(_pattern_second, r'_\1', name)
    name = re.sub(_pattern_third, r'\1_\2', name)
    return name.lower()


def cameldict_to_snake_case(camel: dict) -> dict:
    """
    Converts a dictionary with camel case keys to a dictionary with snake case key.
    :param camel: the camel case dictionary
    :return: the corresponding snake case dictionary
    """
    if camel is None or len(camel) == 0:
        return camel

    result = {}
    for k, v in camel.items():
        if isinstance(v, dict):
            v = cameldict_to_snake_case(v)
        elif isinstance(v, list):
            t = []
            for e in v:
                if isinstance(e, dict):
                    t.append(cameldict_to_snake_case(e))
                else:
                    t.append(e)
            v = t
        result[camel_to_snake_case(k)] = v

    return result
