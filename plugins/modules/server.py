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
module: server

short_description: manage Avantra servers

description:
- You can create, delete or update servers in Avantra.
- Start, stop, restart servers using Avantra functionality.
- A server is always identified with its C(server_name) and C(customer_name).

options:
    exists_state:
        description:
        - If C(present) the server with the given parameter is created in case is does
          not exist or modified in case it exists.
        - If C(absent) the server identified by the I(server_name) and I(customer_name)
          is deleted if it exists.
        choices:
        - present
        - absent
        default: present
        type: str
    server_name:
        description: The name to identify the server.
        required: true
        type: str
    customer_name:
        description: The customer name to identify the server.
        required: true
        type: str
    fqdn_or_ip_address:
        description:
        - Configures how the server can be reached over the network. Can be an IP address or a host name.
        - If C(exists_state=present) and the server has to be created this parameter is mandatory.
        required: false
        type: str
    dns_domain:
        description:
        - Configures the DNS domain for this server.
        - This has to a domain registered in Avantra.
        type: str
        required: false
    host_aliases:
        description: A list of valid host aliases.
        type: list
        elements: str
        required: false
    description:
        description: The description for the server.
        required: false
        type: str
    notes:
        description: The notes for the server.
        required: false
        type: str
    credentials:
        description: >
            Add credentials to this server. See the examples for more information on how
            to set the different credential types. The key for the child objects is one of the credential
            keys found in Avantra.
        type: dict
        required: false

    run_state:
        description:
        - If C(started) and the current state is C(run_state=stopped) or C(run_state=unknown) the server will
          be started.
        - If C(stopped) and the current state is C(run_state=started) or C(run_state=unknown) the server will
          be started.
        - B(Note:) if C(exists_state=absent) and the server exists the run state change will be applied before
          the server is deleted. If C(exists_state=present) the run state change will be executed after the server
          has been created.
        type: str
        choices:
            - started
            - stopped
    run_options:
        description:
        - Allows you to configure the behaviour of the run_state changes.
        type: dict
        required: false
        default: {}
        suboptions:
            always_execute:
                 description:
                 - Ignore the current state and just execute the start/stop.
                 required: false
                 type: bool
                 default: false
            monitoring:
                 description:
                 - If C(run_state=started) this parameter defaults to true.
                 - If C(run_state=stopped) this parameter defaults to false.
                 - If C(run_state=restarted) this parameter is ignored.
                 type: bool
            wait_seconds:
                description:
                - Defines the wait time in seconds after a server start before executing next steps.
                required: false
                default: 60
                type: int
            force_stop:
                description:
                - Avantra checks for known running applications (ie. applications with monitoring turned on) and cancels
                  a stop if some are found. With C(force_stop=true), the server will be stopped in any case.
                required: false
                default: true
                type: bool
            execution_name:
                description:
                - Defines a name for the action to be executed.
                required: false
                type: str

extends_documentation_fragment:
    - avantra.core.auth_options.token
    - avantra.core.seealso
    - avantra.core.authors
    - avantra.core.check_mode_unsupported
    - avantra.core.option_monitoring
    - avantra.core.option_timezone
    - avantra.core.option_custom_attributes
    - avantra.core.option_system_role
    - avantra.core.version_added_23_0
    - avantra.core.notes_ansiblevaults
    - avantra.core.option_application_type
"""

EXAMPLES = r"""
- name: Create Server if it doesn't exist
  avantra.core.server:
    exists: present
    server_name: "agent_5432"
    customer_name: "Avantra 1"
    fqdn_or_ip_address: "host5432"
    system_role: "Test"
    host_aliases:
      - host-5432
    credentials:
      avantra.basic:
        cred_type: basic
        username: <username>
        password: <password>
      avantra.abc:
        cred_type: ssh
        username: <username>
        password: <password>
        hostname: home
        port: 4321
        config:
          ssh_option1: <value>

# Start an existing server
- name: Start Server
  avantra.core.server:
    server_name: "agent_54323"
    customer_name: "Avantra 1"
    run_state: started
    run_options:
      always_execute: true
"""

RETURN = r"""
server:
    description:
    - If C(exists_state=present) and the server can be identified the system information is returned.
    type: dict
    returned: present
"""

from datetime import datetime, timedelta

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    parse_api_date_time
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.server import (
    create_server,
    delete_server,
    fetch_server,
    update_server,
    turn_monitoring_off,
    turn_monitoring_on
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.system_actions import (
    SERVER_START,
    SERVER_STOP,
    execute_system_action
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    create_argument_spec,
    AVANTRA_TOKEN,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    AvantraAnsibleModule
)


def _get_server_run_state(server):
    if server is not None:
        # At the moment there is no way to tell what is the correct run_state of a SAP system. Here
        # we check whether there is a SystemAlive check not older than 10 minutes.
        checks = server.pop("checks", None)
        if len(checks) > 0 and hasattr(checks[0], "last_refresh"):
            last_refresh = parse_api_date_time(checks[0]["last_refresh"])
            if last_refresh > datetime.now() - timedelta(minutes=10) and checks[0]["last_refresh"] == "OK":
                return "started"

    return "unknown"


def ensure_server_started(module, server, result):
    prev_run_state = _get_server_run_state(server)
    result["diff"]["before"]["run_state"] = prev_run_state

    run_options = module.params.get("run_options")
    if prev_run_state != "started" or run_options.get("always_execute"):
        result["action_result"] = execute_system_action(
            module,
            SERVER_START,
            system_id=server["id"],
            execution_name=run_options["execution_name"],
            args={
                "SET_MONI_ON": run_options.get("monitoring", True),
                "WAIT_SECONDS": run_options.get("wait_seconds")
            }
        )
        result["diff"]["after"]["run_state"] = "started"
        result["changed"] = True


def ensure_server_stopped(module, server, result):
    prev_run_state = _get_server_run_state(server)
    result["diff"]["before"]["run_state"] = prev_run_state

    run_options = module.params.get("run_options")
    if prev_run_state != "stopped" or run_options.get("always_execute"):
        result["action_result"] = execute_system_action(
            module,
            SERVER_STOP,
            system_id=server["id"],
            execution_name=run_options["execution_name"],
            args={
                "SET_MONI_OFF": run_options.get("monitoring", False),
                "FORCE_STOP": run_options.get("force_stop")
            }
        )
        result["diff"]["after"]["run_state"] = "stopped"
        result["changed"] = True


def ensure_server_monitoring(module, server, result):
    if server["monitor_off"] == "true":
        prev_monitoring = True
    else:
        prev_monitoring = False

    monitoring = module.params.get("monitoring")

    if monitoring is not None and prev_monitoring != monitoring:
        if monitoring:
            success, msg, server_after = turn_monitoring_on(module, server["id"])
        else:
            success, msg, server_after = turn_monitoring_off(module, server["id"])

        if success:
            server = server_after

    return server


def ensure_server_present(module, customer_name, server_name):
    result = {
        "changed": False
    }

    success, msg, server = fetch_server(module,
                                        server_name=server_name,
                                        customer_name=customer_name)

    if server is None:
        prev_exists_state_state = "absent"
    else:
        prev_exists_state_state = "present"

    diff = {
        "before": {
            "exists_state": prev_exists_state_state,
            "server": server
        },
        "after": {
            "exists_state": "present",
        }
    }

    if prev_exists_state_state == "absent":

        if module.params.get("system_role") is None:
            module.fail_json(msg="system_role argument is missing (it is needed when a server has to be created)",
                             result=result)

        if module.params.get("fqdn_or_ip_address") is None:
            module.fail_json(
                msg="fqdn_or_ip_address argument is missing (it is needed when a server has to be created)",
                result=result)

        success, msg, server = create_server(module, customer_name=customer_name, server_name=server_name)
        if success:
            module.log(f"Server '{server_name}' created successfully")
            result.update(changed=True, server=server)

        else:
            module.fail_json(msg=msg, result=result)

    else:
        success, msg, server = update_server(module, server_system_id=server.get("id"))
        if success:
            diff["after"]["server"] = server
            result.update(
                changed=True,
                server=server
            )
        else:
            module.fail_json(msg=msg, result=result)

    result["diff"] = diff

    server = ensure_server_monitoring(module, server, result)

    run_state = module.params.get("run_state")
    if run_state == "started":
        ensure_server_started(module, server, result)
    elif run_state == "stopped":
        ensure_server_stopped(module, server, result)
    # elif run_state == "restarted":
    #     ensure_server_restarted(module, server, result)
    else:
        pass

    diff["after"]["server"] = server
    result["server"] = server

    return result


def ensure_server_absent(module, customer_name, server_name):
    result = {
        "changed": False
    }

    success, msg, server = fetch_server(module, server_name=server_name, customer_name=customer_name)

    if server is None:
        prev_exists_state_state = "absent"
    else:
        prev_exists_state_state = "present"

    diff = {
        "before": {
            "exists_state": prev_exists_state_state,
            "server": server
        },
        "after": {
            "exists_state": "absent",
            "server": None
        }
    }
    result["diff"] = diff

    if prev_exists_state_state == "present":

        run_state = module.params.get("run_state")
        if run_state == "started":
            ensure_server_started(module, server, result)
        elif run_state == "stopped":
            ensure_server_stopped(module, server, result)
        # elif run_state == "restarted":
        #     ensure_server_restarted(module, server, result)
        else:
            pass

        success, msg = delete_server(module, server["id"])
        if success:
            result["changed"] = True
        else:
            module.fail_json(msg=msg, result=result)

    return result


def run_module():
    result = {}

    argument_spec = create_argument_spec()
    argument_spec.update({
        "exists_state": dict(type='str', choices=["present", "absent"], default="present"),
        "run_state": dict(type='str', choices=["started", "stopped"]),
        "run_options": dict(type='dict', default={},
                            options=dict(
                                always_execute=dict(type="bool", default=False),
                                monitoring=dict(type="bool"),
                                wait_seconds=dict(type='int', default=60),
                                force_stop=dict(type='bool', default=True),
                                execution_name=dict(type='str'))),
        "server_name": dict(type='str', required=True),
        "customer_name": dict(type='str', required=True),
        "credentials": dict(type='dict'),
        "description": dict(type='str'),
        "monitoring": dict(type='bool'),
        "dns_domain": dict(type='str'),
        "host_aliases": dict(type='list', elements="str"),
        "application_type": dict(type='str'),
        "fqdn_or_ip_address": dict(type='str'),
        "system_role": dict(type='str'),
        "timezone": dict(type='str'),
        "notes": dict(type='str'),
        "custom_attributes": dict(type='dict', default={})
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD)
        ],
        required_one_of=[
            (AVANTRA_API_USER, AVANTRA_TOKEN)
        ]
    )

    # TODO:
    if module.check_mode:
        module.exit_json(**result)

    server_name = module.params.get("server_name")
    customer_name = module.params.get("customer_name")

    exists_state_state = module.params.get("exists_state").lower()
    if exists_state_state == "present":
        result = ensure_server_present(module, customer_name, server_name)
    elif exists_state_state == "absent":
        result = ensure_server_absent(module, customer_name, server_name)
    else:
        module.fail_json(msg="Wrong exists_state state: {0}".format(exists_state_state))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
