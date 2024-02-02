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

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    _compute_avantra_auth_url,
    _compute_avantra_graphql_url,
    create_argument_spec)

import pytest


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


def _assert_equals_str(expected, actual):
    assert expected == actual, "{0} != {1}".format(expected, actual)


def test_compute_avantra_auth_url():
    _assert_equals_str(_compute_avantra_auth_url("test"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/auth"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/auth/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/graphql"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/graphql/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/auth"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/auth/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/graphql"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/graphql/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/auth"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/auth/"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/graphql"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/graphql/"), "http://test/api/auth")


def test_compute_avantra_graphql_url():
    _assert_equals_str(_compute_avantra_graphql_url("test"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("test/api"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("test/api/"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("test/api/auth"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("test/api/auth/"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("test/api/graphql"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("test/api/graphql/"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test/api"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test/api/"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test/api/auth"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test/api/auth/"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test/api/graphql"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("https://test/api/graphql/"), "https://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test"), "http://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test/api"), "http://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test/api/"), "http://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test/api/auth"), "http://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test/api/auth/"), "http://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test/api/graphql"), "http://test/api/graphql")
    _assert_equals_str(_compute_avantra_graphql_url("http://test/api/graphql/"), "http://test/api/graphql")


def test_default_create_argument_spec():
    default_argument_spec = create_argument_spec()
    assert default_argument_spec == dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=False),
        avantra_api_password=dict(type='str', required=False, no_log=True),
        token=dict(type='str', required=False, no_log=True)
    )


def test_no_token_create_argument_spec():
    default_argument_spec = create_argument_spec(allow_token=False)
    assert default_argument_spec == dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=True),
        avantra_api_password=dict(type='str', required=True, no_log=True)
    )
