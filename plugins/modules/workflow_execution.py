#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Avantra

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

from string import Template

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    cameldict_to_snake_case,
    dict_get
)


from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    create_argument_spec,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    AvantraAnsibleModule,
    soap_security_header
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

DOCUMENTATION = r"""
---
module: workflow_execution

short_description: execute Avantra workflows

version_added: "23.0.1"

description: 
- Allow you to trigger Avantra workflows and setting the input variables. 
- It is not possible to stop or cancel the execution using this module.

options:
    name:
        description:
        - Select workflow name to execute
        type: str
        required: true
    namespace:
        description:
        - Select the namespace of the workflow namespace to execute. 
        - I(name) and I(namespace) identify the workflow that is executed.
        type: str
        required: true
    variant:
        description:
        - You can select a specific workflow variant to execute.
        type: str
        required: false
    ignore_default_variant:
        description:
        - If there is a default I(variant) configured for the selected workflow it can be ignored 
          with C(ignore_default_variant=false).
        type: bool
        required: true
        default: false
    args:
        description:
        - "Allows you to define the input parameters for the workflow to start in the form C(key: value)."
        type: dict
        required: false
    
extends_documentation_fragment:
    - avantra.core.auth_options
    - avantra.core.seealso
    - avantra.core.authors
    - avantra.core.check_mode_unsupported    
"""

EXAMPLES = r"""
- name: "Workflow Start"
  avantra.core.workflow_execution:
    name: call_api
    namespace: demo
    args:
      user: <user>
      pw: <password>
      data1: <data1>        
"""

RETURN = r'''
execution_id:
    description: The ID of the triggered execution.
    type: str
    returned: success
    sample: '457'
'''


def run_module():

    result = {
        "changed": False
    }

    argument_spec = create_argument_spec(allow_token=False)
    argument_spec.update({
        "name": dict(type='str', required=True),
        "namespace": dict(type='str', required=True),
        "variant": dict(type='str'),
        "ignore_default_variant": dict(type='str', default=False),
        "args": dict(type="dict", default={})
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

    result["execution_id"] = dict_get(module.send_soap_request(soap), "Envelope", "Body", "StartAutomationWorkflowResponse", "executionId")
    result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
