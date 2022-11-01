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
    AvantraAnsibleModule,
    ERROR_ELEMENT_NOT_FOUND
)

from ansible_collections.avantra.core.plugins.module_utils.snake_case import (
    cameldict_to_snake_case
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
module: sapsystem_get

short_description: load SAP system information

version_added: "23.0.0"

description: >
    This module allows to load information about a SAP system from Avantra. 
    A SAP system can either be fetched using the unified SAP SID together with
    the customer name or just the system's well known ID.

options:
    system_id:
        description: > 
            A system ID for a SAP system. If the ID is not given then the 
            options I(unified_sap_sid), I(customer_name) have to be set.
        required: false
        type: str
    unified_sap_sid:
        description: > 
            The unified SAP SID of the SAP system. If the I(system_id) is set 
            this option will be ignored.
        required: false
        type: str
    customer_name:
        description: The name of the customer the SAP system belongs to.
        required: false
        type: str
    fail_if_not_found:
        description: Whether the task should fail in case the SAP system can not be found.
        required: false
        type: bool
        default: True

notes: 
    - this module can be used to check whether a SAP system exists before creating or deleting it.
        
extends_documentation_fragment:
    - avantra.core.auth_options.token
    - avantra.core.seealso
    - avantra.core.author_mis
    - avantra.core.check_mode_unsupported
'''

EXAMPLES = r'''
# Find a SAP system given its system ID and a fetched authentication token and print the result
- name: Get SAP system with ID 1001
  avantra.core.sapsystem_get:          
    avantra_token: "{{auth.token}}"
    system_id: 1001
  register: get_sapsystem_1001

- name: Print SAP system 1001 data
  ansible.builtin.debug:
    var: get_sapsystem_1001
    
    
# Find a SAP system given its unified SAP SID and a customer name
- name: Get SAP system with ID 1001
  avantra.core.sapsystem_get:          
    avantra_token: "{{auth.token}}"
    unified_sap_sid: AVA_DBG
    customer_name: "My Customer"
  register: get_sapsystem_ava_dgb

- name: Print SAP system AVA_DBG data
  ansible.builtin.debug:
    var: get_sapsystem_ava_dgb
'''

RETURN = r'''
sap_system:
    description: The SAP system if it was found.
    type: dict
    returned: success
    sample: 
        sap_system:
            administrator:
            administrator_deputy:
            application_type: Generic
            assigned_sla:
            avantra_transport_version: 23.0.0.0
            basis_release: '7.40'
            check_count: 0
            component_version:
            credentials:
                - id: avantra.sapControl
                  password: REDACTED
                  private_key:
                  private_key_passphrase:
                  purpose:
                      id: "-7"
                      key: sapControl
                      name: SAP Control User
                  sap_control_user: smaadm
                - id: avantra.sap
                  password: aaaa
                  purpose:
                      id: '5'
                      key: sap
                      name: SAP
                  rfc_user: aaaa
                - basic_user: sapsa
                  id: avantra.abapDbSchema
                  password: REDACTED
                  purpose:
                      id: "-4"
                      key: abapDbSchema
                      name: ABAP DB Schema User
            custom_attributes: []
            custom_data:
            customer:
                id: '4'
                name: mis
            database:
                database_type: SAP_SYBASE_ASE
                dbms_product: SYBASE 16.0.03.09
                id: sapdb-5
                name: SMA
                server:
                    id: '1'
                    name: achnmc-mis
                version: 16.0.03.09
            database_host: golf
            database_monitoring_server:
                id: '1'
                name: achnmc-mis
            database_name: SMA
            database_port: 4901
            database_release: '16.0'
            database_type: SAP ASE
            default_client:
            description: ''
            encoding: U2L
            id: '5'
            maintenance: false
            monitor_level: AUTHENTICATED
            monitor_off: false
            monitor_off_until:
            monitor_switch_date:
            monitor_switch_reason:
            mst: 2
            name: SMA_REMOTE
            operational: true
            operational_since:
            operational_until:
            product_versions:
                - product: SAP SOLUTION MANAGER
                  release: '7.2'
                  short_description: SAP SOLUTION MANAGER 7.2
                  sp_stack: 13 (08/2021) FPS
                  status: INSTALLED
                - product: SLT
                  release: '2.0'
                  short_description: SAP LT REPLICATION SERVER 2.0
                  sp_stack: SP13 (06/2017) SP
                  status: INSTALLED
            real_sap_sid: SMA
            remote: true
            remote_monitoring_server:
                id: '1'
                name: achnmc-mis
            sap_instances_count: 2
            solution_manager:
            spam_patch_level: 740/0082
            status: OK
            status_id: 0
            system_role: Development
            timestamp: '2022-10-12T14:32:27.000+02:00'
            timezone:
            type: SAP_SYSTEM
            unified_sap_sid: SMA_REMOTE
            uuid: 3e7f6884-0bde-46b0-825b-3090df258675    
'''


def run_module():
    result = {}

    argument_spec = create_argument_spec()
    argument_spec.update({
        "system_id": dict(type='str', required=False),
        "unified_sap_sid": dict(type='str', required=False),
        "customer_name": dict(type='str', required=False),
        "fail_if_not_found": dict(type='bool', required=False, default=True)
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
        module.fail_json(rc=ERROR_ELEMENT_NOT_FOUND, msg=f"Unknown argument setup")

    module.exit_json(**result)


def _load_by_system_id(module: AvantraAnsibleModule) -> Dict:
    system_id = module.params["system_id"]
    result: dict = module.send_graphql_request(query=ID_QUERY, variables={"id": system_id})
    sap_system = dict_get(result, "data", "sapSystem")
    if module.params["fail_if_not_found"] and sap_system is None:
        module.fail_json(rc=ERROR_ELEMENT_NOT_FOUND,
                         msg=f"SAP system for ID {system_id} could not be found", result=result)

    return cameldict_to_snake_case({"sapSystem": sap_system})


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
                rc=ERROR_ELEMENT_NOT_FOUND,
                msg=f"SAP system for Unified SAP SID '{unified_sap_sid}' and the customer name '{customer_name}' "
                    f"could not be found", result=result)

    return cameldict_to_snake_case({"sapSystem": systems[0]})


def main():
    run_module()


if __name__ == '__main__':
    main()
