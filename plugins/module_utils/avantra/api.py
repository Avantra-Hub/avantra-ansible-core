from __future__ import (absolute_import, division, print_function)

from typing import Dict, Any
from enum import Enum
from string import Template
from datetime import datetime, timedelta, timezone

from uuid import uuid1
from base64 import b64encode

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (dict_get, xmldict)

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

        self.avantra_token = self.params.get("avantra_token")

    @property
    def avantra_token(self):
        """ Returns the Avantra API token. """
        return self._avantra_api_token

    @avantra_token.setter
    def avantra_token(self, token):
        self._avantra_api_token = token

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

        if self.avantra_token is None:
            self.avantra_token = self.login()

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
                                   "Authorization": f"Bearer {self.avantra_token}",
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

    def login(self: AnsibleModule) -> str:
        url = self.params.get("avantra_api_url", "")
        user = self.params.get("avantra_api_user", "")
        password = self.params.get("avantra_api_password", "")

        auth_url = _compute_avantra_auth_url(url)
        # module.fail_json(msg=f"Computed the authentication URL: {auth_url}")

        auth_data = {
            "username": user,
            "password": password
        }

        resp, info = fetch_url(module=self,
                               url=auth_url + "/login",
                               data=self.jsonify(auth_data),
                               headers={'Content-type': 'application/json'},
                               method="POST")

        status_code = info["status"]
        if status_code != 200:
            return self.fail_json(rc=1001, **info)
        else:
            return self.from_json(resp.read())["token"]

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
        sap_systems = _get(result, "data", "sapSystem")

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
