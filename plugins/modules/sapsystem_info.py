#!/usr/bin/python
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

DOCUMENTATION = r"""
---
module: sapsystem_info

short_description: load information about SAP system

description: >
    This module allows to load information about a SAP system from Avantra.
    The SAP system information can be obtained using the B(Unified SAP SID) together with
    a customer name.

options:
    unified_sap_sid:
        description:
        - The Unified SAP SID of the SAP system. Together with C(customer_name) it identifies the SAP system.
        required: true
        type: str
    customer_name:
        description:
        - A customer name known by Avantra. Together with C(unified_sap_sid) it identifies the SAP system.
        required: true
        type: str
    fail_if_not_found:
        description:
        - Whether the task should fail in case the SAP system can not be found.
        required: false
        type: bool
        default: false

extends_documentation_fragment:
    - avantra.core.auth_options.token
    - avantra.core.seealso
    - avantra.core.authors
    - avantra.core.version_added_23_0
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
sap_system:
    description:
    - If the SAP system can be identified the system information is returned.
    type: dict
    returned: present
"""

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    create_argument_spec,
    AVANTRA_TOKEN,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    AvantraAnsibleModule,
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.sapsystem import (
    fetch_sapsystem
)


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
