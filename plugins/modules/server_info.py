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
module: server_info

short_description: load server information

description:
- This module allows to load information about a server from Avantra.
- The server information can be obtained using the C(server_name) together with a C(customer_name).

options:
    server_name:
        description:
        - The name of the server. Together with C(customer_name) it identifies the server.
        required: true
        type: str
    customer_name:
        description:
        - A customer name known by Avantra. Together with C(server_name) it identifies the server.
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

"""

RETURN = r"""

"""

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


def run_module():
    result = {}

    argument_spec = create_argument_spec()
    argument_spec.update({
        "server_name": dict(type='str', required=True),
        "customer_name": dict(type='str', required=True),
        "fail_if_not_found": dict(type='bool', default=False),
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
