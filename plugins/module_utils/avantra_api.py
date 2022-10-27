from __future__ import (absolute_import, division, print_function)

from typing import Dict, Any
from enum import Enum
from string import Template
from datetime import datetime, timedelta, timezone

from uuid import uuid1
from base64 import b64encode

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

from ansible_collections.avantra.core.plugins.module_utils.xml import (
    xmldict
)

AVANTRA_API_URL = "avantra_api_url"
AVANTRA_API_USER = "avantra_api_user"
AVANTRA_API_PASSWORD = "avantra_api_password"

AVANTRA_TOKEN = "avantra_token"

ERROR_NOT_IMPLEMENTED = 1010
ERROR_ELEMENT_NOT_FOUND = 1011

ERROR_DELETE_ELEMENT_SERVER = 1100
ERROR_DELETE_ELEMENT_SAP_SYSTEM = 1102


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


class SystemActions(Enum):
    SERVER_START = 20
    SERVER_STOP = 21
    # SERVER_RESTART = 20
    SAP_SYSTEM_START = 1
    SAP_SYSTEM_STOP = 2
    SAP_SYSTEM_RESTART = 201
    SAP_SYSTEM_WITH_DB_START = 32
    SAP_SYSTEM_WITH_DB_STOP = 33
    SAP_SYSTEM_WITH_DB_RESTART = 202
    SAP_SYSTEM_WITH_DB_AND_HANA_START = 34
    SAP_SYSTEM_WITH_DB_AND_HANA_STOP = 35
    SAP_SYSTEM_WITH_DB_AND_HANA_RESTART = 203
    SAP_SYSTEM_WITH_DB_AND_SERVER_START = 36
    SAP_SYSTEM_WITH_DB_AND_SERVER_STOP = 37
    SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART = 204


class AvantraAnsibleModule(AnsibleModule):
    """
    Specialized version of the AnsibleModule.
    """

    def __init__(self, argument_spec, bypass_checks=False, no_log=False, mutually_exclusive=None,
                 required_together=None, required_one_of=None, add_file_common_args=False, supports_check_mode=False,
                 required_if=None, required_by=None):
        super().__init__(argument_spec, bypass_checks, no_log, mutually_exclusive, required_together, required_one_of,
                         add_file_common_args, supports_check_mode, required_if, required_by)

        self._avantra_api_token = None
        self._avantra_api_url = None

    @property
    def avantra_token(self):
        """ Returns the Avantra API token. """
        if self._avantra_api_token is None:
            if AVANTRA_TOKEN not in self.params:
                self._avantra_api_token = login(self)
            else:
                self._avantra_api_token = self.params[AVANTRA_TOKEN]

        return self._avantra_api_token

    @property
    def avantra_graphql_url(self):
        """ Returns the Avantra API endpoint as URL strings. """
        if self._avantra_api_url is None:
            self._avantra_api_url = _compute_avantra_graphql_url(self.params.get("avantra_api_url", ""))
        return self._avantra_api_url

    @property
    def avantra_soap_url(self):
        """ Returns the Avantra API endpoint as URL strings. """
        if self._avantra_api_url is None:
            self._avantra_api_url = _compute_avantra_soap_url(self.params.get("avantra_api_url", ""))
        return self._avantra_api_url

    def send_soap_request(self, soap: str) -> Dict:
        """
        Send a SOAP request to the Avantra API
        :param soap:
        :return:
        """
        resp, info = fetch_url(module=self,
                               url=self.avantra_soap_url,
                               data=soap,
                               headers={
                                   "Content-type": "text/xml;charset=UTF-8",
                                   "SOAPAction": ""
                               },
                               method="POST")

        status_code = info["status"]
        if status_code != 200:
            return self.fail_json(rc=1002, **info)
        else:
            return xmldict(resp.read())

    def send_graphql_request(
            self,
            query: str,
            variables: dict = None,
            operation_name: str = None) -> Dict:
        """
        Send a GraphQL request to the Avantra API
        """
        token = self.avantra_token

        graphql_payload = {"query": query}

        if variables is not None:
            graphql_payload["variables"] = variables

        if operation_name is not None:
            graphql_payload["operationName"] = operation_name

        resp, info = fetch_url(module=self,
                               url=self.avantra_graphql_url,
                               data=self.jsonify(graphql_payload),
                               headers={
                                   "Content-type": "application/json",
                                   "Authorization": f"Bearer {token}",
                               },
                               method="POST")

        status_code = info["status"]
        if status_code != 200:
            return self.fail_json(rc=1002, **info)
        else:
            result = self.from_json(resp.read())
            if "errors" in result:
                return self.fail_json(rc=1008, msg="There were API errors", info=info, result=result)
            return result

    def find_server_system_id(self, server_name: str, customer_name: str, dns_domain: str = None) -> str | None:

        variables = {"server_name": server_name, "customer_name": customer_name}

        result = self.send_graphql_request(
            query="""
            query ServerGetByServerName($server_name: String!, $customer_name: String!) {
                systems(
                    where: {
                        filterBy: [
                            { name: "type", operator: eq, value: "SERVER" }
                            { name: "name", operator: eq, value: $server_name }                            
                            { name: "customer.name", operator: eq, value: $customer_name }
                        ]
                    }
                ) { 
                    id
                    ... on Server {
                        dnsDomain
                    }
                }
            }
            """,
            variables=variables
        )
        servers = dict_get(result, "data", "systems")
        if dns_domain is not None:
            servers = list(filter(lambda s: s.get("dnsDomain") == dns_domain))

        if servers is None or len(servers) == 0:
            return None

        return servers[0].get("id")

    def find_server_by_system_id(self, system_id: str) -> str | None:

        variables = {"id": system_id}

        result = self.send_graphql_request(
            query="""
            query ServerGetByID($id: ID!) {
                server(id: $id) { 
                    id                    
                }
            }
            """,
            variables=variables
        )
        servers = dict_get(result, "data", "server")

        if servers is None or len(servers) == 0:
            return None

        return servers[0].get("id")

    def find_sap_system_id(self, unified_sap_sid: str, customer_name: str) -> str | None:

        variables = {"unified_sap_sid": unified_sap_sid, "customer_name": customer_name}

        result = self.send_graphql_request(
            query="""
            query SapSystemGetByUnifiedSapSid($unified_sap_sid: String!, $customer_name: String!) {
                systems(
                    where: {
                        filterBy: [
                            { name: "type", operator: eq, value: "SAP_SYSTEM" }
                            { name: "name", operator: eq, value: $unified_sap_sid }                            
                            { name: "customer.name", operator: eq, value: $customer_name }
                        ]
                    }
                ) { 
                    id
                }
            }
            """,
            variables=variables
        )
        sap_systems = dict_get(result, "data", "systems")

        if sap_systems is None or len(sap_systems) == 0:
            return None

        return sap_systems[0].get("id")

    def find_sap_system_by_system_id(self, system_id: str) -> str | None:

        variables = {"id": system_id}

        result = self.send_graphql_request(
            query="""
            query SapSystemGetByID($id: ID!) {
                sapSystem(id: $id) { 
                    id                 
                }
            }
            """,
            variables=variables
        )
        sap_systems = dict_get(result, "data", "sapSystem")

        if sap_systems is None or len(sap_systems) == 0:
            return None

        return sap_systems[0].get("id")

    def execute_system_action(self, action: SystemActions, system_id: str, args: dict = None,
                              execution_name: str = None) -> dict:

        mutation = """
            mutation ExecuteSystemAction (
                $actionId: ID!,
                $executionName: String,
                $systemIds: [ID!]!,
                $parameters: [SystemActionParameterInput!]!
            ) {
                executeSystemAction(actionId: $actionId,
                    executionName: $executionName,
                    parameter: $parameters,
                    systemIds: $systemIds) {
                        id
                        name
                        description
                        detail
                        status
                        start
                        system {
                            id 
                            name
                        }
                        log
                        timestamp
                        user {
                            id
                            principal                            
                        }
                        customer {
                            id
                            name
                        }
                }
            
            }
        """
        variables = {
            "actionId": action.value,
            "systemIds": [system_id],
            "parameters": [{"key": k, "value": v} for k, v in args.items()]
        }

        if execution_name is not None:
            variables["executionName"] = execution_name

        result = self.send_graphql_request(mutation, variables=variables)
        action_result = dict_get(result, "data", "executeSystemAction")

        return action_result


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


def _compute_avantra_soap_url(url: str) -> str:
    """
    Computes the SOAP URL to depending on the given URL.
    So for example http://localhost/xn will return http://localhost/xn/ws
    :param url: the given url
    :return: the Avantra SOAP URL derived from the original url.
    """

    if not url.startswith("http"):
        url = "https://" + url

    # Normalize the URL (if it ends with a / remove it)
    if url.endswith("/"):
        url = url[:-1]

    if url.endswith("/api/auth"):
        return url[:-9] + "/ws"
    if url.endswith("/api/graphql"):
        return url[:-12] + "/ws"
    elif url.endswith("/api"):
        return url[:-4] + "/ws"
    elif url.endswith("/ws"):
        return url
    else:
        return url + "/ws"


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

    if allow_token:
        return dict(
            avantra_api_url=dict(type='str', required=True),
            avantra_api_user=dict(type='str', required=False),
            avantra_api_password=dict(type='str', required=False, no_log=True),
            avantra_token=dict(type='str', required=False, no_log=True)
        )
    else:
        return dict(
            avantra_api_url=dict(type='str', required=True),
            avantra_api_user=dict(type='str', required=True),
            avantra_api_password=dict(type='str', required=False, no_log=True),
        )


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


def find_customer_id_by_name(module: AvantraAnsibleModule, customer_name: str) -> int | None:
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

    result = module.send_graphql_request(query=query, variables={"customer_name": customer_name})
    customers = dict_get(result, "data", "customers")
    if customers is None or not isinstance(customers, list) or len(customers) == 0:
        return None
    else:
        return int(customers[0]["id"])


def handle_basic_credentials(module: AvantraAnsibleModule, basic_creds, key: str, cred):
    basic_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "name": cred.get("name"),
        # "shared": cred.get("shared")
    })


def handle_ssh_credentials(module: AvantraAnsibleModule, ssh_creds, key: str, cred):
    config = []
    for k, v in cred.get("config", {}).items():
        config.append({
            "key": k,
            "value": v
        })

    ssh_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "hostname": cred.get("hostname"),
        "port": cred.get("port"),
        # TODO: maybe this is a path read the file???
        "identity": cred.get("identity"),
        "identityPassphrase": cred.get("identityPassphrase"),
        "config": config
    })


def handle_sap_control_credentials(module: AvantraAnsibleModule, sap_control_creds, key, cred):
    sap_control_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "privateKey": cred.get("private_key"),
        "privateKeyPassphrase": cred.get("private_key_passphrase"),
        "certificateChain": cred.get("certificate_chain"),
        "name": cred.get("name"),
        # "shared": cred.get("shared")
    })


def handle_rfc_credentials(module: AvantraAnsibleModule, rfc_creds, key, cred):
    rfc_creds.append({
        "id": key,
        "username": cred.get("username"),
        "password": cred.get("password"),
        "client": cred.get("client"),
        "name": cred.get("name"),
        # "shared": cred.get("shared")
    })


def handle_oauth_client_credentials(module: AvantraAnsibleModule, oauth_client_creds, key, cred):
    module.fail_json(rc=ERROR_NOT_IMPLEMENTED, msg="Handling of OAuth Client credentials is not yet implemented")


def handle_oauth_code_credentials(module: AvantraAnsibleModule, oauth_code_creds, key, cred):
    module.fail_json(rc=ERROR_NOT_IMPLEMENTED, msg="Handling of OAuth Code credentials is not yet implemented")


def handle_credentials(module: AvantraAnsibleModule, credentials: dict) -> dict[CredentialType, list[Any]]:
    """
    Given a credentials dictionary this function converts the found credential information in dicts that the
    GraphQL API can understand.
    :param module:
    :param credentials:
    :return:
    """
    basic_creds = []
    ssh_creds = []
    sap_control_creds = []
    rfc_creds = []
    oauth_client_creds = []
    oauth_code_creds = []
    if credentials is not None and len(credentials) > 0:
        for key, cred in credentials.items():
            if "cred_type" in cred:
                cred_type = str(cred["cred_type"]).upper()
                if cred_type == CredentialType.BASIC.name:
                    handle_basic_credentials(module, basic_creds, key, cred)
                elif cred_type == CredentialType.SSH.name:
                    handle_ssh_credentials(module, ssh_creds, key, cred)
                elif cred_type == CredentialType.SAP_CONTROL.name:
                    handle_sap_control_credentials(module, sap_control_creds, key, cred)
                elif cred_type == CredentialType.RFC.name:
                    handle_rfc_credentials(module, rfc_creds, key, cred)
                elif cred_type == CredentialType.OAUTH2_CLIENT.name:
                    handle_oauth_client_credentials(module, oauth_client_creds, key, cred)
                elif cred_type == CredentialType.OAUTH2_CODE.name:
                    handle_oauth_code_credentials(module, oauth_code_creds, key, cred)
                else:
                    module.fail_json(rc=1007, msg=f"Unhandled credential type '{cred_type}'", result=cred)
            else:
                module.fail_json(rc=1008, msg=f"No cred_type defined for credentials with key '{key}'", result=cred)

    return {
        CredentialType.BASIC: basic_creds,
        CredentialType.SSH: ssh_creds,
        CredentialType.SAP_CONTROL: sap_control_creds,
        CredentialType.RFC: rfc_creds,
        CredentialType.OAUTH2_CLIENT: oauth_client_creds,
        CredentialType.OAUTH2_CODE: oauth_code_creds
    }


def handle_custom_attributes(module: AnsibleModule, target: dict, custom_attributes: dict):
    if custom_attributes is not None and len(custom_attributes) > 0:
        target["customAttributes"] = []
        for k, v in custom_attributes.items():
            target["customAttributes"].append({
                "id": k,
                "name": k,
                "value": v
            })


SOAP_SECURITY_HEADER = Template("""
    <soapenv:Header>
        <wsse:Security soapenv:mustUnderstand="1"
                       xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
                       xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
            <wsse:UsernameToken wsu:Id="UsernameToken-${message_id}">
                <wsse:Username>${username}</wsse:Username>
                <wsse:Password
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">${password}</wsse:Password>
                <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">
                    ${nonce}
                </wsse:Nonce>
                <wsu:Created>${timestamp_created}</wsu:Created>
            </wsse:UsernameToken>
            <wsu:Timestamp wsu:Id="TS-${message_id}">
                <wsu:Created>${timestamp_created}</wsu:Created>
                <wsu:Expires>${timestamp_expires}</wsu:Expires>
            </wsu:Timestamp>
        </wsse:Security>
    </soapenv:Header>
""")


def soap_security_header(username: str, password: str) -> str:
    message_id = str(uuid1())
    timestamp_created = datetime.now(timezone.utc)
    timestamp_expires = timestamp_created + timedelta(seconds=60)
    nonce = b64encode(message_id.encode("ascii")).decode("ascii")
    return SOAP_SECURITY_HEADER.substitute(
        username=username,
        password=password,
        message_id=message_id,
        nonce=nonce,
        timestamp_created=timestamp_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        timestamp_expires=timestamp_expires.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
