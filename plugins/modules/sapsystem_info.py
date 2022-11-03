#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    create_argument_spec,
    AVANTRA_TOKEN,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    AvantraAnsibleModule,
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.sapsystem import (
    fetch_sapsystem
)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: sapsystem_info

short_description: load SAP system information

version_added: "23.0.1"

description: >
    This module allows to load information about a SAP system from Avantra. 
    The SAP system information can be obtained using the B(Unified SAP SID) together with
    a customer name.

options:    
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
        
extends_documentation_fragment:
    - avantra.core.auth_options.token
    - avantra.core.seealso
    - avantra.core.authors
'''

EXAMPLES = r'''
# Find a SAP system given its unified SAP SID and a customer name
- name: Get SAP system AVA_DBG
  avantra.core.sapsystem_info:          
    unified_sap_sid: AVA_DBG
    customer_name: "My Customer"
    
# Fail if the SAP system can not be found
- name: Get SAP system AVA_DBG
  avantra.core.sapsystem_info:          
    unified_sap_sid: AVA_DBG
    customer_name: "My Customer"
    fail_if_not_found: true
'''

RETURN = r'''
sap_system:
    description: 
    - If the SAP system can be identified the system information is returned.
    type: dict
    returned: present
'''


def run_module():
    result = {
        "changed": False
    }

    argument_spec = create_argument_spec()
    argument_spec.update({
        "unified_sap_sid": dict(type='str', required=True),
        "customer_name": dict(type='str', required=True),
        "fail_if_not_found": dict(type='bool', default=False)
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD),
            ("unified_sap_sid", "customer_name")
        ],
    )

    if module.check_mode:
        module.exit_json(**result)

    customer_name = module.params.get("customer_name")
    unified_sap_sid = module.params.get("unified_sap_sid")

    success, msg, sap_system = fetch_sapsystem(module, unified_sap_sid=unified_sap_sid, customer_name=customer_name)

    if module.params.get("fail_if_not_found") and not success:
        module.fail_json(msg=msg, result=result)
    else:
        result["sap_system"] = sap_system

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
