# -*- coding: utf-8 -*-

# Copyright 2022 Avantra

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

from string import Template

from ansible_collections.avantra.core.plugins.module_utils.avantra.customer import (
    fetch_customer
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    cameldict_to_snake_case,
    dict_get,
    format_api_date_time
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.credentials import (
    CredentialType,
    handle_credentials
)


def create_server(module, server_name, customer_name):
    # Fetch the customer by name. This could be improved by allowing customer
    # name segments to allow to fetch directly sub-customer ... something like "A/B/C"
    success, msg, customer = fetch_customer(module, customer_name)
    if not success:
        return success, msg, None

    # Prepare the input
    server_input = {"customerId": customer["id"]}

    def _assign(key, query_key=None, only_if_not_none=False):
        if query_key is None:
            query_key = key
        if only_if_not_none:
            if module.params[key] is not None:
                server_input[query_key] = module.params[key]
        else:
            server_input[query_key] = module.params[key]

    server_input["name"] = server_name
    _assign("description", only_if_not_none=True)
    _assign("notes", only_if_not_none=True)
    _assign("fqdn_or_ip_address", "ipAddress")
    _assign("system_role", "systemRole")
    _assign("timezone", only_if_not_none=True)
    _assign("dns_domain", only_if_not_none=True)
    _assign("application_type", "applicationType", only_if_not_none=True)
    _assign("host_aliases", "dnsAliases", only_if_not_none=True)

    if module.params.get("monitoring") is None:
        server_input["monitoring"] = True
    else:
        server_input["monitoring"] = module.params.get("monitoring")

    custom_attributes = module.params["custom_attributes"]
    if custom_attributes is not None and len(custom_attributes) > 0:
        server_input["customAttributes"] = []
        for k, v in custom_attributes.items():
            server_input["customAttributes"].append({
                "id": k,
                "name": k,
                "value": v
            })

    credentials = handle_credentials(module, module.params["credentials"])

    create_server = module.send_graphql_request(
        query=CREATE_MUTATION,
        variables={
            "input": server_input,
            "basicCredentials": credentials.get(CredentialType.BASIC),
            "sshCredentials": credentials.get(CredentialType.SSH),
            # "sapControlCredentials": credentials.get(CredentialType.SAP_CONTROL),
            # "rfcCredentials": credentials.get(CredentialType.RFC),
            # "oauthCodeCredentials": credentials.get(CredentialType.OAUTH2_CODE),
            # "oauthClientCredentials": credentials.get(CredentialType.OAUTH2_CLIENT),
        }
    )

    op_result = dict_get(create_server, "data", "createServer", "result")
    server = dict_get(create_server, "data", "createServer", "server")
    if op_result is None:
        return False, "Could not create the server", None
    elif not op_result["success"]:
        return False, op_result["message"], None
    else:
        return True, "Successfully created the server", cameldict_to_snake_case(server)


def update_server(module, server_system_id):

    # Prepare the input
    server_input = {"id": server_system_id}

    def _assign(key, query_key=None):
        if query_key is None:
            query_key = key
        if module.params[key] is not None:
            server_input[query_key] = module.params[key]

    _assign("description")
    _assign("notes")
    _assign("fqdn_or_ip_address", "ipAddress")
    # _assign("monitoring")
    _assign("system_role", "systemRole")
    _assign("timezone")
    _assign("dns_domain")
    _assign("application_type", "applicationType")
    # Merge lists?
    _assign("host_aliases", "dnsAliases")

    custom_attributes = module.params["custom_attributes"]
    if custom_attributes is not None and len(custom_attributes) > 0:
        server_input["customAttributes"] = []
        for k, v in custom_attributes.items():
            server_input["customAttributes"].append({
                "id": k,
                "name": k,
                "value": v
            })

    credentials = handle_credentials(module, module.params["credentials"])

    update_server = module.send_graphql_request(
        query=UPDATE_MUTATION,
        variables={
            "input": server_input,
            "basicCredentials": credentials.get(CredentialType.BASIC),
            "sshCredentials": credentials.get(CredentialType.SSH),
            # "sapControlCredentials": credentials.get(CredentialType.SAP_CONTROL),
            # "rfcCredentials": credentials.get(CredentialType.RFC),
            # "oauthCodeCredentials": credentials.get(CredentialType.OAUTH2_CODE),
            # "oauthClientCredentials": credentials.get(CredentialType.OAUTH2_CLIENT),
        }
    )

    op_result = dict_get(update_server, "data", "updateServer", "result")
    server = dict_get(update_server, "data", "updateServer", "server")
    if op_result is None:
        return False, "Could not update the server", None
    elif not op_result["success"]:
        return False, op_result["message"], None
    else:
        return True, "Successfully updated the server", cameldict_to_snake_case(server)


def delete_server(module, server_id):
    delete_sap_system = module.send_graphql_request(
        query="""mutation DeleteServer($id: ID!) {
                deleteServer(input: { id: $id }) {
                    result {
                        success
                        message
                        code
                    }
                }
            }
        """,
        variables={
            "id": server_id
        }
    )

    op_result = dict_get(delete_sap_system, "data", "deleteServer", "result")
    if op_result is None:
        return False, "Could not delete the server with ID {0}".format(server_id)
    else:
        return op_result.get("success"), op_result.get("message")


def fetch_server(
        module,
        server_name,
        customer_name,
        remove_checks=False
):
    variables = {
        "server_name": server_name,
        "customer_name": customer_name
    }

    result = module.send_graphql_request(
        query=FETCH_QUERY,
        variables=variables
    )
    servers = dict_get(result, "data", "systems")

    if servers is None or len(servers) == 0:
        return False, "Server can not be found server_name={0} customer_name={1}" \
            .format(server_name, customer_name), None

    server = cameldict_to_snake_case(servers[0])

    if remove_checks:
        server.pop("checks", None)

    return True, "Successfully fetched server", server


def turn_monitoring_off(module, server_id,
                        note=None,
                        cascade=False,
                        until=None
                        ):
    until_str = None
    if until is not None:
        until_str = format_api_date_time(until)

    turn_off_result = module.send_graphql_request(
        query=MONI_OFF_MUTATION,
        variables={
            "id": server_id,
            "note": note,
            "cascade": cascade,
            "until": until_str
        }
    )

    server = dict_get(turn_off_result, "data", "turnMonitoringOffForServer")
    if server is None:
        return False, "Could not turn off monitoring for the server with ID {0}".format(server_id), None
    else:
        return True, "Turned off monitoring for the server with ID {0}".format(server_id), server


def turn_monitoring_on(module, server_id,
                       note=None,
                       cascade=False
                       ):
    turn_on_result = module.send_graphql_request(
        query=MONI_ON_MUTATION,
        variables={
            "id": server_id,
            "note": note,
            "cascade": cascade
        }
    )

    server = dict_get(turn_on_result, "data", "turnMonitoringOnForServer")
    if server is None:
        return False, "Could not turn on monitoring for the server with ID {0}".format(server_id), None
    else:
        return True, "Turned on monitoring for the server with ID {0}".format(server_id), server


FRAGMENT = """
    id
    mst
    checks(where: {
            filterBy: [
                {name: "name" operator: eq value:"AGENTALIVE"}
            ]
        }) {
        id
        name
        status
        lastRefresh
    }
    customAttributes {
        id
        name
        value
    }
    customData
    customer {
        id
        name
    }
    description
    maintenance
    monitorOff
    monitorOffUntil
    monitorSwitchReason
    monitorSwitchDate
    name
    operational
    operationalSince
    operationalUntil
    status
    statusId
    systemRole
    type
    timestamp
    uuid
    ipAddress
    dnsAliases
    dnsDomain
    physicalMemory
    filesystemTotalSize
    filesystemTotalUsed
    sapHardwareKey
    osType
    osPlatform
    osName
    osLongName
    osVersion
    osArchitecture
    notes
    virtualClusterServer
    aliveStatus
    aliveLastUpdate
    aliveSince
    javaDetails {
        extern {
            key
            value
        }
        externVersion
        externJavaHome
        intern {
            key
            value
        }
        internVersion
        # 			scanTime
    }
    cpuDetails {
        name
        model
        vendor
        mhz
        totalCores
    }
    cloudDetails {
        name
        type
    }
    gateway
    natTraversal
    publicKey
    applicationType
    rtmStatus
    rtmDate
    timezone
    # 		nodeOf
    # 		nodes
    # 		activeNode
    # 		sapInstances
    sapInstanceCount
    # 		sapSystems
    sapSystemCount
    # 		cloudServices
    cloudServiceCount
    # 		businessObjects
    businessObjectCount
    # 		databases
    databaseCount
    # 		actions
    # 		performance
    agentVersion
    administrator {
        id
        principal
        firstname
        lastname
        email
        emailAlternative
    }
    administratorDeputy {
        id
        principal
        firstname
        lastname
        email
        emailAlternative
    }
    remote
    #         info
    assignedSLA {
        id
        name
    }
    # 		cloudServiceAuthentication
    monitorLevel
    credentials {
        id
        purpose {
            key
            id
            name
        }
        ... on BasicAuthenticationCredentials {
            basicUser: username
            password
        }
        ... on RfcAuthenticationCredentials {
            rfcUser: username
            password
        }
        ... on SapControlCredentials {
            sapControlUser: username
            password
            privateKey
            privateKeyPassphrase
        }
        ... on SshCredentials {
            hostname
            port
            username
            password
            identity
            identityPassphrase
        }
    }
"""

FETCH_QUERY = Template("""
        query ServerGetByName($$server_name: String!, $$customer_name: String!) {
            systems(
                where: {
                    filterBy: [
                        { name: "type", operator: eq, value: "SERVER" }
                        { name: "name", operator: eq, value: $$server_name }
                        { name: "customer.name", operator: eq, value: $$customer_name }
                    ]
                }
            ) {
                ... on Server {
                    ${fragment}
                }
            }
        }""").substitute(fragment=FRAGMENT)

CREATE_MUTATION = Template("""
    mutation CreateServer(
        $$input: CreateServerInput!
        $$basicCredentials: [SetBasicCredentialsInput!] = []
        $$sshCredentials: [SetSshCredentialsInput!] = []
    ) {

        createServer(input: $$input) {
            result {
                success
                message
                code
            }

            credentials {
                setBasicCredentials(input: $$basicCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setSshCredentials(input: $$sshCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
            }


            server {
                ${fragment}
            }
        }

    }
""").substitute(fragment=FRAGMENT)

UPDATE_MUTATION = Template("""
    mutation UpdateServer(
        $$input: UpdateServerInput!
        $$basicCredentials: [SetBasicCredentialsInput!] = []
        $$sshCredentials: [SetSshCredentialsInput!] = []
    ) {

        updateServer(input: $$input) {
            result {
                success
                message
                code
            }

            credentials {
                setBasicCredentials(input: $$basicCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setSshCredentials(input: $$sshCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
            }


            server {
                ${fragment}
            }
        }

    }
""").substitute(fragment=FRAGMENT)


MONI_OFF_MUTATION = Template("""
    mutation TurnMonitoringOffForServer($$id: ID!, $$cascade: Boolean, $$note: String, $$until) {
        turnMonitoringOffForServer(
            id: $$id
            cascade: $$cascade
            note: $$note
            until: $$until
        ) {
            ${fragment}
        }
    }
""").substitute(fragment=FRAGMENT)

MONI_ON_MUTATION = Template("""
    mutation TurnMonitoringOnForServer($$id: ID!, $$cascade: Boolean, $$note: String) {
        turnMonitoringOnForServer(
            id: $$id
            cascade: $$cascade
            note: $$note
        ) {
            ${fragment}
        }
    }
""").substitute(fragment=FRAGMENT)
