# -*- coding: utf-8 -*-

# Copyright Avantra

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
