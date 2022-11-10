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


def create_sapsystem(module, unified_sap_sid, customer_name):
    # Fetch the customer by name. This could be improved by allowing customer
    # name segments to allow to fetch directly sub-customer ... something like "A/B/C"
    success, msg, customer = fetch_customer(module, customer_name)
    if not success:
        return success, msg, None

    # Prepare the input
    sap_system_input = {"customerId": customer["id"]}

    def _assign(key, query_key=None, only_if_not_none=False):
        if query_key is None:
            query_key = key
        if only_if_not_none:
            if module.params[key] is not None:
                sap_system_input[query_key] = module.params[key]
        else:
            sap_system_input[query_key] = module.params[key]

    sap_system_input["unifiedSapSid"] = unified_sap_sid
    _assign("real_sap_sid", "realSapSid")
    _assign("description", only_if_not_none=True)
    _assign("notes", only_if_not_none=True)
    _assign("remote_monitoring_entry_point", "remoteMonitoringEntryPoint")
    _assign("remote_monitoring_server_system_id", "remoteMonitoringServerSystemId")
    _assign("system_role", "systemRole")
    _assign("timezone", only_if_not_none=True)
    _assign("application_type", "applicationType", only_if_not_none=True)

    if module.params.get("monitoring") is None:
        sap_system_input["monitoring"] = True
    else:
        sap_system_input["monitoring"] = module.params.get("monitoring")

    database = module.params["database"]
    if database is not None and len(database) > 0:
        sap_system_input["database"] = {
            "monitoringServerSystemId": database.get("monitoring_server_system_id"),
            "host": database.get("host"),
            "port": database.get("port"),
            "name": database.get("name")
        }

    custom_attributes = module.params["custom_attributes"]
    if custom_attributes is not None and len(custom_attributes) > 0:
        sap_system_input["customAttributes"] = []
        for k, v in custom_attributes.items():
            sap_system_input["customAttributes"].append({
                "id": k,
                "name": k,
                "value": v
            })

    credentials = handle_credentials(module, module.params["credentials"])

    create_sap_system = module.send_graphql_request(
        query=CREATE_MUTATION,
        variables={
            "input": sap_system_input,
            "basicCredentials": credentials.get(CredentialType.BASIC),
            "sshCredentials": credentials.get(CredentialType.SSH),
            "sapControlCredentials": credentials.get(CredentialType.SAP_CONTROL),
            "rfcCredentials": credentials.get(CredentialType.RFC),
            "oauthCodeCredentials": credentials.get(CredentialType.OAUTH2_CODE),
            "oauthClientCredentials": credentials.get(CredentialType.OAUTH2_CLIENT),
        }
    )

    op_result = dict_get(create_sap_system, "data", "createSapSystem", "result")
    sap_system = dict_get(create_sap_system, "data", "createSapSystem", "sapSystem")
    if op_result is None:
        return False, "Could not create the SAP system", None
    elif not op_result["success"]:
        return False, op_result["message"], None
    else:
        return True, "Successfully created the SAP system", cameldict_to_snake_case(sap_system)


def update_sapsystem(module, sap_system_id):

    # Prepare the input
    sap_system_input = {"id": sap_system_id}

    def _assign(key, query_key=None):
        if query_key is None:
            query_key = key

        if module.params[key] is not None:
            sap_system_input[query_key] = module.params[key]

    # sap_system_input["unifiedSapSid"] = unified_sap_sid
    _assign("real_sap_sid", "realSapSid")
    _assign("description")
    _assign("notes")
    _assign("remote_monitoring_entry_point", "remoteMonitoringEntryPoint")
    _assign("remote_monitoring_server_system_id", "remoteMonitoringServerSystemId")
    _assign("monitoring")
    _assign("system_role", "systemRole")
    _assign("timezone")
    _assign("application_type", "applicationType")

    database = module.params["database"]
    if database is not None and len(database) > 0:
        sap_system_input["database"] = {}
        if database.get("monitoring_server_system_id") is not None:
            sap_system_input["database"]["monitoringServerSystemId"] = database.get("monitoring_server_system_id")
        if database.get("host") is not None:
            sap_system_input["database"]["host"] = database.get("host")
        if database.get("port") is not None:
            sap_system_input["database"]["port"] = database.get("port")
        if database.get("name") is not None:
            sap_system_input["database"]["name"] = database.get("name")

    custom_attributes = module.params["custom_attributes"]
    if custom_attributes is not None and len(custom_attributes) > 0:
        sap_system_input["customAttributes"] = []
        for k, v in custom_attributes.items():
            sap_system_input["customAttributes"].append({
                "id": k,
                "name": k,
                "value": v
            })

    credentials = handle_credentials(module, module.params["credentials"])

    create_sap_system = module.send_graphql_request(
        query=UPDATE_MUTATION,
        variables={
            "input": sap_system_input,
            "basicCredentials": credentials.get(CredentialType.BASIC),
            "sshCredentials": credentials.get(CredentialType.SSH),
            "sapControlCredentials": credentials.get(CredentialType.SAP_CONTROL),
            "rfcCredentials": credentials.get(CredentialType.RFC),
            "oauthCodeCredentials": credentials.get(CredentialType.OAUTH2_CODE),
            "oauthClientCredentials": credentials.get(CredentialType.OAUTH2_CLIENT),
        }
    )

    op_result = dict_get(create_sap_system, "data", "updateSapSystem", "result")
    sap_system = dict_get(create_sap_system, "data", "updateSapSystem", "sapSystem")
    if op_result is None:
        return False, "Could not update the SAP system", None
    elif not op_result["success"]:
        return False, op_result["message"], None
    else:
        return True, "Successfully updated the SAP system", cameldict_to_snake_case(sap_system)


def delete_sapsystem(module, sap_system_id):
    delete_sap_system = module.send_graphql_request(
        query="""mutation DeleteSapSystem($id: ID!) {
                deleteSapSystem(input: { id: $id }) {
                    result {
                        success
                        message
                        code
                    }
                }
            }
        """,
        variables={
            "id": sap_system_id
        }
    )

    op_result = dict_get(delete_sap_system, "data", "deleteSapSystem", "result")
    if op_result is None:
        return False, "Could not delete the SAP system with ID {0}".format(sap_system_id)
    else:
        return op_result.get("success"), op_result.get("message")


def fetch_sapsystem(
        module,
        unified_sap_sid,
        customer_name,
        remove_checks=False
):
    variables = {
        "unified_sap_sid": unified_sap_sid,
        "customer_name": customer_name
    }

    result = module.send_graphql_request(
        query=FETCH_QUERY,
        variables=variables
    )
    sap_systems = dict_get(result, "data", "systems")

    if sap_systems is None or len(sap_systems) == 0:
        return False, "SAP system can not be found unified_sap_si={0} " \
                      "customer_name={1}".format(unified_sap_sid, customer_name), None

    sap_system = cameldict_to_snake_case(sap_systems[0])

    if remove_checks:
        sap_system.pop("checks", None)

    return True, "Successfully fetched SAP system", sap_system


def turn_monitoring_off(module,
                        sap_system_id,
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
            "id": sap_system_id,
            "note": note,
            "cascade": cascade,
            "until": until_str
        }
    )

    sap_system = dict_get(turn_off_result, "data", "turnMonitoringOffForSapSystem")
    if sap_system is None:
        return False, "Could not turn off monitoring for the SAP system with ID {0}".format(sap_system_id), None
    else:
        return True, "Turned off monitoring for the SAP system with ID {0}".format(sap_system_id), sap_system


def turn_monitoring_on(module,
                       sap_system_id,
                       note=None,
                       cascade=False
                       ):
    turn_on_result = module.send_graphql_request(
        query=MONI_ON_MUTATION,
        variables={
            "id": sap_system_id,
            "note": note,
            "cascade": cascade
        }
    )

    sap_system = dict_get(turn_on_result, "data", "turnMonitoringOnForSapSystem")
    if sap_system is None:
        return False, "Could not turn on monitoring for the server with ID {0}".format(sap_system_id), None
    else:
        return True, "Turned on monitoring for the server with ID {0}".format(sap_system_id), sap_system


FRAGMENT = """
    id
    mst
    checks(where: {
            filterBy: [
                {name: "name" operator: eq value:"SystemAlive"}
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
    unifiedSapSid
    realSapSid
    applicationType
    timezone
    basisRelease
    componentVersion
    spamPatchLevel
    encoding
    #         defaultClient
    #         databaseName
    #         databaseHost
    #         databasePort
    #         databaseRelease
    #         databaseType
    #         abapUser
    #         abapDatabaseUser
    #         j2eeUser
    #         j2eeDatabaseUser
    #         sapControlUser
    #         sapInstances
    sapInstancesCount
    remoteMonitoringServer {
        id
        name
    }
    databaseMonitoringServer {
        id
        name
    }
    #         actions
    #         performance
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
    productVersions {
        shortDescription
        product
        release
        spStack
        status
    }
    database {
        id
        name
        databaseType
        host
        port
        version
        dbmsProduct
        server {
            id
            name
        }
    }
    remote
    #         info
    assignedSLA {
        id
        name
    }
    solutionManager {
        id
        name
    }
    componentVersion
    avantraTransportVersion
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
            query SapSystemGetByUnifiedSapSid($$unified_sap_sid: String!, $$customer_name: String!) {
                systems(
                    where: {
                        filterBy: [
                            { name: "type", operator: eq, value: "SAP_SYSTEM" }
                            { name: "name", operator: eq, value: $$unified_sap_sid }
                            { name: "customer.name", operator: eq, value: $$customer_name }
                        ]
                    }
                ) {
                ... on SapSystem {
                    ${fragment}
                }
            }
        }""").substitute(fragment=FRAGMENT)

CREATE_MUTATION = Template("""
    mutation CreateSapSystem(
        $$input: CreateSapSystemInput!
        $$basicCredentials: [SetBasicCredentialsInput!] = []
        $$sshCredentials: [SetSshCredentialsInput!] = []
        $$sapControlCredentials: [SetSapControlCredentialsInput!] = []
        $$rfcCredentials: [SetRfcCredentialsInput!] = []
        $$oauthCodeCredentials: [SetOAuthCodeCredentialsInput!] = []
        $$oauthClientCredentials: [SetOAuthClientCredentialsInput!] = []
    ) {
        createSapSystem(input: $$input) {
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

                setSapControlCredentials(input: $$sapControlCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setRfcCredentials(input: $$rfcCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setOAuthCodeCredentials(input: $$oauthCodeCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setOAuthClientCredentials(input: $$oauthClientCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

            }

            sapSystem {
                ${fragment}
            }
        }
    }

""").substitute(fragment=FRAGMENT)

UPDATE_MUTATION = Template("""
    mutation UpdateSapSystem(
        $$input: UpdateSapSystemInput!
        $$basicCredentials: [SetBasicCredentialsInput!] = []
        $$sshCredentials: [SetSshCredentialsInput!] = []
        $$sapControlCredentials: [SetSapControlCredentialsInput!] = []
        $$rfcCredentials: [SetRfcCredentialsInput!] = []
        $$oauthCodeCredentials: [SetOAuthCodeCredentialsInput!] = []
        $$oauthClientCredentials: [SetOAuthClientCredentialsInput!] = []
    ) {
        updateSapSystem(input: $$input) {
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

                setSapControlCredentials(input: $$sapControlCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setRfcCredentials(input: $$rfcCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setOAuthCodeCredentials(input: $$oauthCodeCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

                setOAuthClientCredentials(input: $$oauthClientCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }

            }

            sapSystem {
                ${fragment}
            }
        }
    }

""").substitute(fragment=FRAGMENT)

MONI_OFF_MUTATION = Template("""
    mutation TurnMonitoringOffForSapSystem($$id: ID!, $$cascade: Boolean, $$note: String, $$until: DateTime) {
        turnMonitoringOffForSapSystem(
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
    mutation TurnMonitoringOnForSapSystem($$id: ID!, $$cascade: Boolean, $$note: String) {
        turnMonitoringOnForSapSystem(
            id: $$id
            cascade: $$cascade
            note: $$note
        ) {
            ${fragment}
        }
    }
""").substitute(fragment=FRAGMENT)
