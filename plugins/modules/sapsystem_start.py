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
    AvantraAnsibleModule,
    ERROR_ELEMENT_NOT_FOUND,
    SystemActions
)

__metaclass__ = type

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
        "unified_sap_sid": dict(type='str', required=False),
        "customer_name": dict(type='str', required=False),
        "with_database": dict(type='bool', required=False, default=False),
        "with_servers": dict(type='bool', required=False, default=False),
        "with_system_db_if_hana": dict(type='bool', required=False, default=False),
        "execution_name": dict(type='str', required=False),
        "fail_if_not_found": dict(type='bool', required=False, default=True),
        "check_db_state": dict(type='bool', required=False, default=True),
        "set_monitoring_on": dict(type='bool', required=False, default=True),
        "wait_seconds":  dict(type='int', required=False, default=60),
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

    with_database = module.params["with_database"]
    with_servers = module.params["with_servers"]
    with_system_db_if_hana = module.params["with_system_db_if_hana"]
    if with_servers and module.params["with_system_db_if_hana"]:
        module.fail_json(msg="Unsupported flag combination: only one of ['with_servers', 'with_system_db_if_hana'] "
                             "can be set to true")
    elif with_servers and not with_database:
        module.fail_json(msg="Unsupported flag combination: 'with_database' has to be set to true in case "
                             "'with_servers' is set to true")
    elif with_system_db_if_hana and not with_database:
        module.fail_json(msg="Unsupported flag combination: 'with_database' has to be set to true in case "
                             "'with_system_db_if_hana' is set to true")

    if not with_database:
        action = SystemActions.SAP_SYSTEM_START
    elif with_servers:
        action = SystemActions.SAP_SYSTEM_WITH_DB_AND_SERVER_START
    elif with_system_db_if_hana:
        action = SystemActions.SAP_SYSTEM_WITH_DB_AND_HANA_START
    else:
        action = SystemActions.SAP_SYSTEM_WITH_DB_START

    if module.check_mode:
        module.exit_json(**result)

    system_id = module.params.get("system_id")
    if system_id is None:
        system_id = module.find_sap_system_id(
            unified_sap_sid=module.params.get("unified_sap_sid"),
            customer_name=module.params.get("customer_name")
        )
    else:
        system_id = module.find_sap_system_by_system_id(system_id)

    if system_id is None and module.params["fail_if_not_found"]:
        module.fail_json(rc=ERROR_ELEMENT_NOT_FOUND, msg="Can not find SAP system")

    result["action_result"] = module.execute_system_action(
        action,
        system_id=system_id,
        execution_name=module.params["execution_name"],
        args={
            "SET_MONI_ON": module.params["set_monitoring_on"],
            "WAIT_SECONDS": module.params["wait_seconds"],
            "CHECK_DB_STATE": module.params["check_db_state"]
        }
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
