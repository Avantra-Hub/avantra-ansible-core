from __future__ import (absolute_import, division, print_function)

from ansible_collections.avantra.core.plugins.module_utils.snake_case import (
    camel_to_snake_case,
    cameldict_to_snake_case
)

import pytest
import json


class AnsibleModuleExit(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class ExitJson(AnsibleModuleExit):
    pass


class FailJson(AnsibleModuleExit):
    pass


class FakeAnsibleModule:
    def __init__(self):
        self.params = {}
        self.tmpdir = None

    def exit_json(self, *args, **kwargs):
        raise ExitJson(*args, **kwargs)

    def fail_json(self, *args, **kwargs):
        raise FailJson(*args, **kwargs)


@pytest.fixture
def fake_ansible_module():
    return FakeAnsibleModule()


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
