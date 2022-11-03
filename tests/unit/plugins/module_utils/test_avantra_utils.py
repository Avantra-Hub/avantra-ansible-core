# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)


from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    camel_to_snake_case,
    cameldict_to_snake_case,
    dict_get
)

import json
import pytest


def test_dict_get():
    result = json.loads('{"data": {"sapSystem": {"id": "5", "name": "SMA_REMOTE"}}}')
    assert dict_get(result, "data", "sapSystem") is not None


def test_cameldict_to_snake_case():
    assert camel_to_snake_case("CamelCase") == "camel_case"
    assert camel_to_snake_case("C1amelCase") == "c1amel_case"
    assert camel_to_snake_case("assignedSLA") == "assigned_sla", camel_to_snake_case("assignedSLA") + " != assigned_sla"
    assert camel_to_snake_case("") == ""
    assert camel_to_snake_case(None) is None


def test_cameldict_to_snake_case():
    assert cameldict_to_snake_case(None) is None
    assert cameldict_to_snake_case({}) == {}
    assert cameldict_to_snake_case({
        "CamelCase": True
    }) == {"camel_case": True}
    assert cameldict_to_snake_case({
        "CamelCase": {
            "HelloWorld": "Yes"
        }
    }) == {"camel_case": {"hello_world": "Yes"}}
    print("***")
    assert cameldict_to_snake_case({
        "CamelCase": [
            {"HelloWorld": "Yes"},
            42
        ]
    }) == {"camel_case": [{"hello_world": "Yes"}, 42]}