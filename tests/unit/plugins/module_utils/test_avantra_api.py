from ansible_collections.avantra.core.plugins.module_utils.avantra_api import _compute_avantra_auth_url, \
    create_argument_spec, AVANTRA_API_URL, AVANTRA_API_USER, AVANTRA_API_PASSWORD, AVANTRA_TOKEN

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


def _assert_equals_str(expected: str, actual: str):
    assert expected == actual, f"{expected} != {actual}"


def test_compute_avantra_auth_url():
    _assert_equals_str(_compute_avantra_auth_url("test"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/auth"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/auth/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("test/api/graphql"), "https://test/api/auth")

    _assert_equals_str(_compute_avantra_auth_url("https://test"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/auth"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/auth/"), "https://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("https://test/api/graphql"), "https://test/api/auth")

    _assert_equals_str(_compute_avantra_auth_url("http://test"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/auth"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/auth/"), "http://test/api/auth")
    _assert_equals_str(_compute_avantra_auth_url("http://test/api/graphql"), "http://test/api/auth")


def test_default_create_argument_spec():
    default_argument_spec = create_argument_spec()
    assert default_argument_spec == dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=True),
        avantra_api_password=dict(type='str', required=True, no_log=True),
        avantra_token=dict(type='str', required=False, no_log=True),
        # We don't need the mutually exclusive here as if the token is present it will be taken.
        # mutually_exclusive=[
        #     ("avantra_api_url", "avantra_token"),
        # ],
        required_together=[
            (AVANTRA_API_URL, AVANTRA_API_USER, AVANTRA_API_PASSWORD),
        ],
        required_one_of=[
            (AVANTRA_API_URL, AVANTRA_TOKEN),
        ],
    )


def test_no_token_create_argument_spec():
    default_argument_spec = create_argument_spec(allow_token=False)
    assert default_argument_spec == dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=True),
        avantra_api_password=dict(type='str', required=True, no_log=True)
    )
