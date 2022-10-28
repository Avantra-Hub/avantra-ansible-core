#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)

from typing import Dict

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    login, create_argument_spec,
    ERROR_ELEMENT_NOT_FOUND, ERROR_DELETE_ELEMENT_SERVER,
    AVANTRA_TOKEN, AVANTRA_API_USER,
    AVANTRA_API_PASSWORD, dict_get, find_customer_id_by_name, CredentialType,
    handle_credentials, handle_custom_attributes, AvantraAnsibleModule
)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: customer

short_description: This module handles Avantra customers

version_added: "23.0.0"

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
        "domain": dict(type='dict', required=False),
        "fail_if_not_found": dict(type='bool', required=False, default=True)
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
            ("system_id", "server_name")
        ]
    )

    if module.check_mode:
        module.exit_json(**result)

    system_id = module.params.get("system_id")
    if system_id is None:
        system_id = module.find_server_system_id(
            server_name=module.params.get("server_name"),
            customer_name=module.params.get("customer_name"),
            dns_domain=module.params.get("domain")
        )

    if system_id is None and module.params["fail_if_not_found"]:
        module.fail_json(rc=ERROR_ELEMENT_NOT_FOUND, msg="Can not find server")

    delete_server = module.send_graphql_request(
        query="""mutation DeleteServer($id: ID!) {
                deleteServer(input: { id: $id }) {
                    result {
                        success
                        message
                        code
                    }
                }
            }
        """,
        variables={
            "id": system_id
        }
    )

    op_result = dict_get(delete_server, "data", "deleteServer", "result")
    if op_result is None or not op_result["success"]:
        module.fail_json(rc=ERROR_DELETE_ELEMENT_SERVER, msg="Could not delete server", result=delete_server)

    result["result"] = op_result
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
