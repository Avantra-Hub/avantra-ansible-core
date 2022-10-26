#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)

from typing import Dict

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    login, create_argument_spec,
    AVANTRA_TOKEN, AVANTRA_API_USER,
    AVANTRA_API_PASSWORD, dict_get, find_customer_id_by_name, CredentialType,
    handle_credentials, handle_custom_attributes, AvantraAnsibleModule
)

__metaclass__ = type

CREATE_MUTATION = """
    mutation CreateServer(
        $input: CreateServerInput!
        $basicCredentials: [SetBasicCredentialsInput!] = []
        $sshCredentials: [SetSshCredentialsInput!] = []
    ) {
        
        createServer(input: $input) {
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
            }

            
            server {
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
        "server_name": dict(type='str', required=True),
        "customer_name": dict(type='str', required=True),
        "credentials": dict(type='dict', required=False),
        # NOTE: Add options to define the layout of credentials
        "description": dict(type='str', required=False),
        "monitoring": dict(type='bool', required=False, default=False),
        "dns_domain": dict(type='str', required=False),
        "dns_aliases": dict(type='list', elements="str", required=False),
        "fqdn_or_ip_address": dict(type='str', required=True),
        "application_type": dict(type='str', required=False),
        "system_role": dict(type='str', required=True),
        "timezone": dict(type='str', required=False),
        "notes": dict(type='str', required=False),
        "custom_attributes": dict(type='dict', required=False, default={})
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
    server_input = {"customerId": customer_id}

    def _assign(key: str, query_key: str = None, only_if_not_none: bool = False):
        if query_key is None:
            query_key = key
        if only_if_not_none:
            if module.params[key] is not None:
                server_input[query_key] = module.params[key]
        else:
            server_input[query_key] = module.params[key]

    _assign("server_name", "name")
    _assign("description", only_if_not_none=True)
    _assign("notes", only_if_not_none=True)
    _assign("fqdn_or_ip_address", "ipAddress")
    _assign("monitoring")
    _assign("system_role", "systemRole")
    _assign("timezone", only_if_not_none=True)
    _assign("dns_domain", only_if_not_none=True)
    _assign("application_type", "applicationType", only_if_not_none=True)
    _assign("dns_aliases", "dnsAliases", only_if_not_none=True)

    handle_custom_attributes(module, server_input, module.params["custom_attributes"])

    credentials = handle_credentials(module, module.params["credentials"])

    create_server = module.send_graphql_request(
        query=CREATE_MUTATION,
        variables={
            "input": server_input,
            "basicCredentials": credentials.get(CredentialType.BASIC),
            "sshCredentials": credentials.get(CredentialType.SSH),
        }
    )

    op_result = dict_get(create_server, "data", "createServer", "result")
    server = dict_get(create_server, "data", "createServer", "server")
    if op_result is None or not op_result["success"] or server is None:
        module.fail_json(rc=1006, msg="Could not create the server", result=create_server)

    result = {"server": server}

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
