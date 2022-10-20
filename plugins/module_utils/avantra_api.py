import contextlib
from typing import Dict

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

AVANTRA_API_URL = "avantra_api_url"
AVANTRA_API_USER = "avantra_api_user"
AVANTRA_API_PASSWORD = "avantra_api_password"

AVANTRA_TOKEN = "avantra_token"


def _compute_avantra_auth_url(url: str) -> str:
    """
    Computes the authentication URL to depending on the given URL.
    So for example http://localhost/xn will return http://localhost/xn/api/auth.
    :param url: the given url
    :return: the Avantra authentication URL derived from the original url.
    """

    if not url.startswith("http"):
        url = "https://" + url

    # Normalize the URL (if it ends with a / remove it)
    if url.endswith("/"):
        url = url[:-1]

    if url.endswith("/api/auth"):
        return url
    elif url.endswith("/api"):
        return url + "/auth"
    elif url.endswith("/graphql"):
        return url[:-8] + "/auth"
    else:
        return url + "/api/auth"


def login(module: AnsibleModule) -> str:
    """
    Executes a login to the Avantra API return the API token used to execute the request.
    :param module:
    :return:
    """
    url = module.params.get("avantra_api_url", "")
    user = module.params.get("avantra_api_user", "")
    password = module.params.get("avantra_api_password", "")

    auth_url = _compute_avantra_auth_url(url)
    # module.fail_json(msg=f"Computed the authentication URL: {auth_url}")

    auth_data = {
        "username": user,
        "password": password
    }

    resp, info = fetch_url(module=module,
                           url=auth_url + "/login",
                           data=module.jsonify(auth_data),
                           headers={'Content-type': 'application/json'},
                           method="POST")

    status_code = info["status"]
    if status_code != 200:
        return module.fail_json(**info)
    else:
        return module.from_json(resp.read())["token"]


# allow the user to get a context object with login already executed. the context
# offers the available API functions like create SAP system, create Server and so on!


def create_argument_spec(allow_token: bool = True) -> Dict:
    """
    Returns the default argument_spec as dict to be used with an AnsibleModule.
    :param allow_token: if true a ansible_token is allowed as alternative to the
                        other API variables.

    :return: the argument_spec as dict
    """

    result = dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=True),
        avantra_api_password=dict(type='str', required=True, no_log=True)
    )

    if allow_token:
        result.update(
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

    return result


def send_graphql_request(query: str, variables: dict):
    pass
