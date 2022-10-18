import contextlib

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from contextlib import contextmanager


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
        return str(info)
    else:
        return module.from_json(resp.read())["token"]


# allow the user to get a context object with login already executed. the context
# offers the available API functions like create SAP system, create Server and so on!

