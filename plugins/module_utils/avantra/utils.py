# -*- coding: utf-8 -*-

# Copyright 2022 Avantra

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from xml.etree import ElementTree
from io import StringIO
from collections import defaultdict
import re
from datetime import datetime

_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

_pattern_first = re.compile('(.)([A-Z][a-z]+)')
_pattern_second = re.compile('__([A-Z])')
_pattern_third = re.compile('([a-z0-9])([A-Z])')


def dict_get(value, *keys):
    """
    Tries to access a nested key within potential nested dictionaries.
    :param value: the dict to access
    :param keys: the path of properties to get
    :return: the value at the path defined by the keys or None if it can not be found.
    """
    result = None

    current_dict = value

    for key in keys:
        if key in current_dict:
            result = current_dict[key]
            if isinstance(result, dict):
                current_dict = result
        else:
            return None

    return result


def _etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(_etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def xmldict(xml):
    it = ElementTree.iterparse(StringIO(xml.decode("UTF-8")))
    for evt, el in it:
        before, sep, el.tag = el.tag.rpartition('}')  # strip ns
    return _etree_to_dict(it.root)


def camel_to_snake_case(camel=""):
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


def cameldict_to_snake_case(camel):
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


def parse_api_date_time(date_time_str):
    if date_time_str is None:
        return datetime.now()
    return datetime.strptime(date_time_str, _DATETIME_FORMAT)


def format_api_date_time(dt=datetime.now()):
    return dt.strftime(_DATETIME_FORMAT)
