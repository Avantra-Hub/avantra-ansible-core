#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)

from typing import Dict

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    create_argument_spec,
    login,
    AVANTRA_TOKEN,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    dict_get,
    find_customer_id_by_name,
    CredentialType,
    handle_credentials,
    handle_custom_attributes,
    AvantraAnsibleModule
)


from ansible_collections.avantra.core.plugins.module_utils.sapsystem import (
    create_sapsystem,
    update_sapsystem,
    delete_sapsystem,
    fetch_sapsystem,
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
module: sapsystem_create

short_description: create a SAP system

version_added: "23.0.0"

description: >
    This module offers the functionality to create SAP systems on the Avantra server.

options:
    unified_sap_sid:
        description: > 
            The unified SAP SID of the SAP system.
        required: true
        type: str
    real_sap_sid:
        description: > 
            The real SAP SID of the SAP system.
        required: true
        type: str
    customer_name:
        description: The name of the customer the SAP system should be added to.
        required: true
        type: str
    description:
        description: The description for the SAP system.
        required: false
        type: str
    notes:
        description: The notes for the SAP system.
        required: false
        type: str
    application_type:
        description: the application type (on of the defined in the customizations).
        required: false        
        type: str
    system_role:
        description: configures the system role.
        choices:        
            - Consolidation
            - Development
            - Education
            - Integration
            - Production
            - Quality assurance
            - Sandpit
            - Test
            - ... customized roles
                    
        required: true
        type: str
    timezone:
        description: configures the timezone
        required: false
        type: str            
    monitoring:
        description: Should the monitoring be turned on or off after the creation of the SAP system.
        required: false
        default: false
        type: bool
    database:
        description: configures the database
        required: false
        type: dict
        suboptions:
            monitoring_server_system_id:
                description: the system ID of the server monitoring the database.
                type: str
                required: false
            host:
                description: defines the database host.
                type: str
                required: false
            port:
                description: defines the database port.
                type: str
                required: false            
            name:
                description: configures the database name.
                type: str
                required: false            
    
    credentials:
        description: > 
            add credentials to this SAP system. See the examples for more information on how 
            to set the different credential types. The key for the child objects are the credential
            keys found in Avantra.
        type: dict
        required: false    
    
    remote_monitoring_entry_point:
        description: configures the remote entrypoint for agentless SAP system.
        type: str  
        required: false
        
    remote_monitoring_server_system_id:
        description: configures the server monitoring the remote SAP system.
        type: str  
        required: false
    
    custom_attributes:
        description: >
            custom attributes for the SAP system as key value pairs. See 
            U(https://docs.avantra.com/product-guide/latest/avantra/custom-attributes.html) 
            for an explanation. 
        required: false
        type: dict
        
extends_documentation_fragment:
    - avantra.core.auth_options.token
    - avantra.core.seealso
    - avantra.core.author_mis
    - avantra.core.check_mode_unsupported    
'''

EXAMPLES = r'''
# Complete example of how to create an SAP system. Including the check whether the
# system is already present. 
- name: Try to find SAP system AVA_EXA
  avantra.core.sapsystem_get:
       avantra_token: "{{auth.token}}"
       unified_sap_sid: "AVA_EXA"
       customer_name: "Example Customer"
       fail_if_not_found: false
  register: result_get   

- name: Create SAP system
  avantra.core.sapsystem_create:
    avantra_token: "{{auth.token}}"
    unified_sap_sid: "AVA_EXA"
    real_sap_sid: "EXA"
    customer_name: "Example Customer"
    system_role: "Development"
    timezone: "UTC"
    monitoring: true
    notes: "Some notes"
    description: "A description"
    database:
      monitoring_server_system_id: 253
      host: "golf"
      name: "EXA"
      port: 12345
    credentials:
      # SAP control user
      avantra.sapControl:
        cred_type: sap_control
        username: <user>
        password: <password>     
      # ABAP user
      avantra.defaultRfcUser:
        cred_type: rfc
        username: <user>
        password: <password>
        client: 000       
      # ABAP database user
      avantra.abapDbSchema:
        cred_type: basic
        username: <user>
        password: <password>
      # J2EE user
      avantra.j2eeUser:
        cred_type: basic
        username: <user>
        password: <password>
      # J2EE database user
      avantra.javaDbSchema:
        cred_type: basic
        username: <user>
        password: <password>
    register: create_sapsystem
  when: result_get.sap_system is undefined or result_get.sap_system == None

- name: Print return information from the previous task
  ansible.builtin.debug:
    var: create_sapsystem

'''

RETURN = r'''
extends_documentation_fragment:
    - avantra.core.sapsystem_return
'''


def run_module():
    result = {}

    argument_spec = create_argument_spec()
    argument_spec.update({
        "exist": dict(type='str', required=False, choices=["present", "absent"], default="present"),
        "run": dict(type='str', required=False, choices=["started", "stopped", "restarted"]),
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

    exist_state = module.params.get("exist").lower()
    if exist_state == "present":
        pass
    elif exist_state == "absent":


        pass
    else:
        module.fail_json(msg="Wrong exist state: {0}".format(exist_state))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
