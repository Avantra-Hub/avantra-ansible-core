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
    dict_get,
    AvantraAnsibleModule
)

__metaclass__ = type

ID_QUERY = """
    query SapSystemGet($id: ID!) {
        sapSystem(id: $id) {
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
"""

SID_QUERY = """
    query SapSystemGetByUnifiedSapSid(
        $unified_sap_sid: String!
        $customer_name: String!
    ) {
        systems(
            where: {
                filterBy: [
                    { name: "type", operator: eq, value: "SAP_SYSTEM" }
                    { name: "name", operator: eq, value: $unified_sap_sid }
                    { name: "customer.name", operator: eq, value: $customer_name }
                ]
            }
        ) {
            ... on SapSystem {
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
        "system_id": dict(type='int', required=False),
        "unified_sap_sid": dict(type='str', required=False),
        "customer_name": dict(type='str', required=False),
        "fail_if_not_found": dict(type='bool', required=False, default=True),
        "args": dict(required=False, default={}),
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD),
            ("unified_sap_sid", "customer_name")
        ],
        required_one_of=[
            (AVANTRA_API_USER, AVANTRA_TOKEN),
            ("system_id", "unified_sap_sid"),
        ]
    )

    if module.check_mode:
        module.exit_json(**result)

    if "system_id" in module.params and module.params["system_id"] is not None:
        result = _load_by_system_id(module)
    elif "unified_sap_sid" in module.params and "customer_name" in module.params:
        result = _load_by_unified_sap_sid(module)
    else:
        module.fail_json(rc=1004, msg=f"Unknown argument setup")

    module.exit_json(**result)


def _load_by_system_id(module: AvantraAnsibleModule) -> Dict:
    system_id = module.params["system_id"]
    result: dict = module.send_graphql_request(query=ID_QUERY, variables={"id": system_id})
    sap_system = dict_get(result, "data", "sapSystem")
    if module.params["fail_if_not_found"] and sap_system is None:
        module.fail_json(rc=1003, msg=f"SAP system for ID {system_id} could not be found: {result}")

    return {"sapSystem": sap_system}


def _load_by_unified_sap_sid(module: AvantraAnsibleModule) -> Dict:
    unified_sap_sid = module.params["unified_sap_sid"]
    customer_name = module.params["customer_name"]
    result: dict = module.send_graphql_request(
        query=SID_QUERY,
        variables={"unified_sap_sid": unified_sap_sid,
                   "customer_name": customer_name}
    )
    systems = dict_get(result, "data", "systems")
    if systems is None or len(systems) == 0:
        systems = [None]

    if module.params["fail_if_not_found"]:
        if systems[0] is None:
            module.fail_json(
                rc=1003,
                msg=f"SAP system for Unified SAP SID '{unified_sap_sid}' and the customer name '{customer_name}' "
                    f"could not be found: {result}")

    return {"sapSystem": systems[0]}


def main():
    run_module()


if __name__ == '__main__':
    main()
