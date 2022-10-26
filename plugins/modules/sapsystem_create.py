#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)

from typing import Dict

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    login, create_argument_spec,
    AVANTRA_TOKEN, AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    dict_get, find_customer_id_by_name, CredentialType,
    handle_credentials, handle_custom_attributes, AvantraAnsibleModule
)

__metaclass__ = type

CREATE_MUTATION = """
    mutation CreateSapSystem(
        $input: CreateSapSystemInput!
        $basicCredentials: [SetBasicCredentialsInput!] = []
        $sshCredentials: [SetSshCredentialsInput!] = []
        $sapControlCredentials: [SetSapControlCredentialsInput!] = []
        $rfcCredentials: [SetRfcCredentialsInput!] = []
        $oauthCodeCredentials: [SetOAuthCodeCredentialsInput!] = []
        $oauthClientCredentials: [SetOAuthClientCredentialsInput!] = []
    ) {
        createSapSystem(input: $input) {
            result {
                success
                message
                code
            }
    
            credentials {
                setBasicCredentials(input: $basicCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
    
                setSshCredentials(input: $sshCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
                
                setSapControlCredentials(input: $sapControlCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
                
                setRfcCredentials(input: $rfcCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
                
                setOAuthCodeCredentials(input: $oauthCodeCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
                
                setOAuthClientCredentials(input: $oauthClientCredentials) {
                    result {
                        code
                        success
                        message
                    }
                }
                
            }
    
            sapSystem {
                id
                mst
                #         checks
                checkCount
                #         checkCountSummary
                #         checksRelay
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
                defaultClient
                databaseName
                databaseHost
                databasePort
                databaseRelease
                databaseType
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
                    # 					databaseHost
                    # 					databasePort
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
            }
        }
    }

"""

DOCUMENTATION = r'''
---
module: customer

short_description: This module handles Avantra customers

version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - avantra.core.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  avantra.core.customer:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  avantra.core.customer:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  avantra.core.customer:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''


def run_module():
    result = {}

    argument_spec = create_argument_spec()
    argument_spec.update({
        "unified_sap_sid": dict(type='str', required=True),
        "real_sap_sid": dict(type='str', required=True),
        "customer_name": dict(type='str', required=True),
        "credentials": dict(type='dict', required=False),
        "description": dict(type='str', required=False),
        "monitoring": dict(type='bool', required=False, default=False),
        "application_type": dict(type='str', required=False),
        "system_role": dict(type='str', required=True),
        "timezone": dict(type='str', required=False),
        "notes": dict(type='str', required=False),
        "custom_attributes": dict(type='dict', required=False, default={}),
        "remote_monitoring_entry_point": dict(type='str', required=False),
        "remote_monitoring_server_system_id": dict(type='str', required=False),
        "database": dict(
            type="dict",
            required=False,
            options=dict(
                monitoring_server_system_id=dict(type="str", required=False),
                host=dict(type="str", required=False),
                port=dict(type="str", required=False),
                name=dict(type="str", required=False)
            )),
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD)
        ],
        required_one_of=[
            (AVANTRA_API_USER, AVANTRA_TOKEN)
        ]
    )

    if module.check_mode:
        module.exit_json(**result)

    # Fetch the customer by name. This could be improved by allowing customer
    # name segments to allow to fetch directly sub-customer ... something like "A/B/C"
    customer_name = module.params["customer_name"]
    customer_id = find_customer_id_by_name(module, customer_name)
    if customer_id is None:
        module.fail_json(rc=1005, msg=f"Customer with name '{customer_name}' could not be found")

    # Prepare the input
    sap_system_input = {"customerId": customer_id}

    def _assign(key: str, query_key: str = None, only_if_not_none: bool = False):
        if query_key is None:
            query_key = key
        if only_if_not_none:
            if module.params[key] is not None:
                sap_system_input[query_key] = module.params[key]
        else:
            sap_system_input[query_key] = module.params[key]

    _assign("unified_sap_sid", "unifiedSapSid")
    _assign("real_sap_sid", "realSapSid")
    _assign("description", only_if_not_none=True)
    _assign("notes", only_if_not_none=True)
    _assign( "remote_monitoring_entry_point", "remoteMonitoringEntryPoint")
    _assign("remote_monitoring_server_system_id", "remoteMonitoringServerSystemId")
    _assign("monitoring")
    _assign("system_role", "systemRole")
    _assign("timezone", only_if_not_none=True)
    _assign("application_type", "applicationType", only_if_not_none=True)

    database = module.params["database"]
    if database is not None and len(database) > 0:
        sap_system_input["database"] = {
            "monitoringServerSystemId": database.get("monitoring_server_system_id"),
            "host": database.get("host"),
            "port": database.get("port"),
            "name": database.get("name")
        }

    handle_custom_attributes(module, sap_system_input, module.params["custom_attributes"])

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
    if op_result is None or not op_result["success"] or sap_system is None:
        module.fail_json(rc=1006, msg="Could not create the SAP system", result=create_sap_system)

    result = {"sapSystem": sap_system}

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
