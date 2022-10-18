#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import login


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
    try:
        out = open('/Users/mis/dev/collections/ansible_collections/avantra/core/avantra-ansible-module.log', 'a',
                   encoding="utf-8")
        out.write(f"{datetime.now()} |ansible.core.customer |MODULE "
                  f"|------------------------------------------------------------\n")
        out.write(f"{datetime.now()} |ansible.core.customer |MODULE |run_module()\n")

        # define available arguments/parameters a user can pass to the module
        module_args = dict(
            # name=dict(type='str', required=True),
            # new=dict(type='bool', required=False, default=False),
            avantra_api_url=dict(type='str', required=True),
            avantra_api_user=dict(type='str', required=True),
            avantra_api_password=dict(type='str', required=True)
        )

        out.write(f"{datetime.now()} |ansible.core.customer |MODULE |module_args={module_args}\n")

        # seed the result dict in the object
        # we primarily care about changed and state
        # changed is if this module effectively modified the target
        # state will include any data that you want your module to pass back
        # for consumption, for example, in a subsequent task
        result = dict(
            changed=False,
            original_message='',
            message=''
        )

        out.write(f"{datetime.now()} |ansible.core.customer |MODULE |result={result}\n")

        # the AnsibleModule object will be our abstraction working with Ansible
        # this includes instantiation, a couple of common attr would be the
        # args/params passed to the execution, as well as if the module
        # supports check mode
        module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
        )

        out.write(f"{datetime.now()} |ansible.core.customer |MODULE |test module_utils: {login(module)}\n")

        out.write(f"{datetime.now()} |ansible.core.customer |MODULE |module.params={module.params}\n")

        for p in module.params:
            out.write(f"{datetime.now()} |ansible.core.customer |MODULE |{p}\n")

    except Exception as e:
        out.write(e)

    finally:
        out.flush()
        out.close()

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)




    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['original_message'] = module.params['name']
    result['message'] = 'goodbye'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if module.params['new']:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
