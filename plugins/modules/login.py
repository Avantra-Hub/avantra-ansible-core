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
module: login

short_description: authentication operations

description: >
    With this module a authentication token can be fetched from an defined
    Avantra API endpoint url together with a valid username and password.
    You can then use the token for other tasks.

extends_documentation_fragment:
    - avantra.core.auth_options
    - avantra.core.seealso
    - avantra.core.authors
    - avantra.core.check_mode_unsupported
    - avantra.core.version_added_23_0
"""

EXAMPLES = r"""
# Authenticate against endpoint and print registered token
- name: Authenticate against Avantra API
  avantra.core.login:
    avantra_api_url: https://avantra-ui/xn
    avantra_api_user: <username>
    avantra_api_password: <password>
  register: auth

- name: Print the authentication token
  ansible.builtin.debug:
    var: auth

- name: Get information about a server
  avantra.core.server_info:
    token: "{{auth.token}}"
    server_name: aservername
    customer_name: acustomername

"""

RETURN = r"""
token:
    description: The token to be used during a playbook.
    type: str
    returned: success
    sample: eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJtaXMyIiwicm9sZXMiOltdLCJpYXQiOjE2NjY4OTg3NzEsImV4cCI6MTY2NjkyMDM3MX0...
"""

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    AvantraAnsibleModule
)


def run_module():
    module_args = dict(
        avantra_api_url=dict(type='str', required=True),
        avantra_api_user=dict(type='str', required=True),
        avantra_api_password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        token=None
    )

    module = AvantraAnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    result["token"] = module.login()
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
