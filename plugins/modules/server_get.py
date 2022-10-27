#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)

from typing import Dict

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    login, create_argument_spec,
    AVANTRA_TOKEN, AVANTRA_API_USER,
    AVANTRA_API_PASSWORD, dict_get,
    AvantraAnsibleModule
)

__metaclass__ = type

ID_QUERY = """
    query ServerGet($id: ID!) {
        server(id: $id) {
            id
            mst
            #         checks
            #         checkCount
            #         checkCountSummary
            #         checksRelay
            customAttributes {
                id
                name
                value
            }
            #         customData
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
        }
    }
"""

SID_QUERY = """
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
            ... on Server {
                id
                mst
                #         checks
                #         checkCount
                #         checkCountSummary
                #         checksRelay
                customAttributes {
                    id
                    name
                    value
                }
                #         customData
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
        "system_id": dict(type='str', required=False),
        "server_name": dict(type='str', required=False),
        "customer_name": dict(type='str', required=False),
        "fail_if_not_found": dict(type='bool', required=False, default=True),
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD),
            ("server_name", "customer_name")
        ],
        required_one_of=[
            (AVANTRA_API_USER, AVANTRA_TOKEN),
            ("system_id", "server_name"),
        ]
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    if "system_id" in module.params and module.params["system_id"] is not None:
        result = _load_by_system_id(module)
    elif "server_name" in module.params and "customer_name" in module.params:
        result = _load_by_server_name(module)
    else:
        module.fail_json(rc=1004, msg=f"Unknown argument setup")

    module.exit_json(**result)


def _load_by_system_id(module: AvantraAnsibleModule) -> Dict:
    system_id = module.params["system_id"]
    result: dict = module.send_graphql_request(query=ID_QUERY, variables={"id": system_id})
    server = dict_get(result, "data", "server")
    if module.params["fail_if_not_found"] and server is None:
        module.fail_json(rc=1003, msg=f"Server for ID {system_id} could not be found: {result}")

    return {"server": server}


def _load_by_server_name(module: AvantraAnsibleModule) -> Dict:
    server_name = module.params["server_name"]
    customer_name = module.params["customer_name"]
    result: dict = module.send_graphql_request(
        query=SID_QUERY,
        variables={"server_name": server_name,
                   "customer_name": customer_name}
    )
    servers = dict_get(result, "data", "systems")
    if servers is None or len(servers) == 0:
        servers = [None]

    if module.params["fail_if_not_found"]:
        if servers[0] is None:
            module.fail_json(rc=1003,
                             msg=f"Server for server name '{server_name}' and customer name '{customer_name}' could "
                                 f"not be found: {result}")

    return {"server": servers[0]}


def main():
    run_module()


if __name__ == '__main__':
    main()
