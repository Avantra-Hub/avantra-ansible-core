#!/usr/bin/python

# Copyright: (c) 2022 Avantra
from __future__ import (absolute_import, division, print_function)

from typing import Dict

from string import Template

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

from ansible_collections.avantra.core.plugins.module_utils.avantra_api import (
    login, create_argument_spec,
    AVANTRA_TOKEN, AVANTRA_API_USER,
    AVANTRA_API_PASSWORD, dict_get,
    AvantraAnsibleModule, soap_security_header
)

__metaclass__ = type

SOAP_WORKFLOW_ARG = Template("<web:args><web:key>${key}</web:key><web:value>${value}</web:value></web:args>")
SOAP_WORKFLOW_ARG_NO_VALUE = Template("<web:args><web:key>${key}</web:key></web:args>")
SOAP_WORKFLOW_VARIANT = Template("<web:variant>${variant}</web:variant>")
SOAP_WORKFLOW_START = Template("""
<soapenv:Envelope 
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:web="http://www.syslink.ch/2013/xandria/webservice">
    ${header} 
   <soapenv:Body>
      <web:StartAutomationWorkflowRequest>
         <web:name>${name}</web:name>
         <web:namespace>${namespace}</web:namespace>
         ${arguments}               
         ${variant}   
         <web:ignoreDefaultVariant>${ignore_default_variant}</web:ignoreDefaultVariant>
      </web:StartAutomationWorkflowRequest>
   </soapenv:Body>
</soapenv:Envelope>
""")

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

    argument_spec = create_argument_spec(allow_token=False)
    argument_spec.update({
        "name": dict(type='str', required=True),
        "namespace": dict(type='str', required=True),
        "variant": dict(type='str', required=False),
        "ignore_default_variant": dict(type='str', required=False, default=False),
        "args": dict(type="dict", required=False, default={})
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD),
        ],
        required_one_of=[
            AVANTRA_API_USER,
        ]
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    variables = {
        "name": module.params.get("name"),
        "namespace": module.params.get("namespace")
    }

    if module.params.get("ignore_default_variant"):
        variables["ignore_default_variant"] = "true"
    else:
        variables["ignore_default_variant"] = "false"

    if module.params.get("variant") is not None:
        variables["variant"] = SOAP_WORKFLOW_VARIANT.substitute(variant=module.params.get("variant"))
    else:
        variables["variant"] = ""

    args = module.params.get("args")
    if args is not None and isinstance(args, dict) and len(args) > 0:
        arguments = []
        for k, v in args.items():

            if v is None:
                arguments.append(SOAP_WORKFLOW_ARG.substitute(key=k, value=""))
            if isinstance(v, bool):
                arguments.append(SOAP_WORKFLOW_ARG.substitute(key=k, value=str(v).lower()))
            else:
                arguments.append(SOAP_WORKFLOW_ARG.substitute(key=k, value=v))
        variables["arguments"] = "\n".join(arguments)
    else:
        variables["arguments"] = ""

    variables["header"] = soap_security_header(
        username=module.params.get("avantra_api_user", ""),
        password=module.params.get("avantra_api_password", "")
    )

    soap = SOAP_WORKFLOW_START.substitute(**variables)

    result["response"] = module.send_soap_request(soap)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
