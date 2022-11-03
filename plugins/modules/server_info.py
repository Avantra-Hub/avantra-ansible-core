#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from ansible_collections.avantra.core.plugins.module_utils.avantra.server import (
    fetch_server
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    create_argument_spec,
    AVANTRA_TOKEN,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    AvantraAnsibleModule
)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: customer

short_description: This module handles Avantra customers

version_added: "23.0.1"

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

    if module.check_mode:
        module.exit_json(**result)

    customer_name = module.params.get("customer_name")
    server_name = module.params.get("server_name")

    success, msg, server = fetch_server(module,
                                        server_name=server_name,
                                        customer_name=customer_name,
                                        remove_checks=True)

    if module.params.get("fail_if_not_found") and not success:
        module.fail_json(msg=msg, result=result)
    else:
        result["server"] = server

    module.exit_json(**result)

def main():
    run_module()


if __name__ == '__main__':
    main()
