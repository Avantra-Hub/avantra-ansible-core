import contextlib
from typing import Dict, Any
from enum import Enum

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

AVANTRA_API_URL = "avantra_api_url"
AVANTRA_API_USER = "avantra_api_user"
AVANTRA_API_PASSWORD = "avantra_api_password"

AVANTRA_TOKEN = "avantra_token"


class SystemType(Enum):
    SERVER = 0
    SAP_INSTANCE = 1
    SAP_SYSTEM = 2
    DATABASE = 3
    BUSINESS_SERVICE = 4
    SAP_BUSINESS_OBJECT = 5
    CLOUD_SERVICE = 6


class CredentialType(Enum):
    BASIC = 0
    OAUTH2_CODE = 1
    OAUTH2_CLIENT = 2
    RFC = 3
    SAP_CONTROL = 4
    SSH = 5


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


def _compute_avantra_graphql_url(url: str) -> str:
    """
    Computes the GraphQL URL to depending on the given URL.
    So for example http://localhost/xn will return http://localhost/xn/api/graphql.
    :param url: the given url
    :return: the Avantra GraphQL URL derived from the original url.
    """

    if not url.startswith("http"):
        url = "https://" + url

    # Normalize the URL (if it ends with a / remove it)
    if url.endswith("/"):
        url = url[:-1]

    if url.endswith("/api/auth"):
        return url[:-9] + "/api/graphql"
    elif url.endswith("/api"):
        return url + "/graphql"
    elif url.endswith("/graphql"):
        return url
    else:
        return url + "/api/graphql"


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
        return module.fail_json(rc=1001, **info)
    else:
        return module.from_json(resp.read())["token"]


# allow the user to get a context object with login already executed. the context
# offers the available API functions like create SAP system, create Server and so on!


def create_argument_spec(allow_token: bool = True) -> Dict:
    """
    Returns the default argument_spec as dict to be used with an AnsibleModule.
    :param allow_token: if true an ansible_token is allowed as alternative to the
                        other API variables.

    :return: the argument_spec as dict
    """

    result = dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=False),
        avantra_api_password=dict(type='str', required=False, no_log=True)
    )

    if allow_token:
        result[AVANTRA_TOKEN] = dict(type='str', required=False, no_log=True)

    return result


def send_graphql_request(
        module: AnsibleModule,
        query: str,
        variables: dict = None,
        operation_name: str = None) -> Dict:
    url = _compute_avantra_graphql_url(module.params.get("avantra_api_url", ""))
    token = module.params.get("avantra_token", "")

    graphql_payload = {"query": query}

    if variables is not None:
        graphql_payload["variables"] = variables

    if operation_name is not None:
        graphql_payload["operationName"] = operation_name

    resp, info = fetch_url(module=module,
                           url=url,
                           data=module.jsonify(graphql_payload),
                           headers={
                               'Content-type': 'application/json',
                               'Authorization': f"Bearer {token}",
                           },
                           method="POST")

    status_code = info["status"]
    if status_code != 200:
        return module.fail_json(rc=1002, **info)
    else:
        # TODO: Check for "errors" parallel to "data"
        return module.from_json(resp.read())


def dict_get(value: dict, *keys) -> Any:
    """

    :param value:
    :param keys:
    :return:
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


# def find_system_by_name_and_customer(
#         module: AnsibleModule,
#         system_type: SystemType,
#         name: str,
#         customer_name: str = None
# ) -> Dict:
#     pass


def find_customer_id_by_name(module: AnsibleModule, customer_name: str) -> int | None:
    """
    Returns the customer ID or None if it can not be found.

    :param module: the current ansible module
    :param customer_name: the customer name to look for.
    :return:
    """

    query = """
    query GetCustomerByName($customer_name: String!) {
        customers(
            where: { filterBy: [{ name: "name", operator: eq, value: $customer_name }] }
        ) {
            id
            name
            sapCustomerNumber
            description
            remarks
            phone
            mobile
            fax
            email
            timezone
            address
            postbox
            postalCode
            city
            country
            timestamp
            customerUrl
            customData
            guid
            parent {
                id
                name
            }
            children {
                id
                name
            }
            childrenCount
        }
    }
    """

    result: dict = send_graphql_request(module, query=query, variables={"customer_name": customer_name})
    customers = dict_get(result, "data", "customers")
    if customers is None or not isinstance(customers, list) or len(customers) == 0:
        return None
    else:
        return int(customers[0]["id"])
