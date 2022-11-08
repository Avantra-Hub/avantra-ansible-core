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
module: sapsystem

short_description: manage SAP systems in Avantra

description:
    - You can create, delete or update SAP systems in Avantra.
    - Start, stop, restart SAP systems using Avantra functionality.
    - A SAP system is always identified with its B(Unified SAP SID) and customer name.

options:
    unified_sap_sid:
        description:
        - The B(Unified SAP SID) of a SAP system. Together with the I(customer_name) parameter it identifies a
          SAP system.
        required: true
        type: str
    customer_name:
        description:
        - A customer name known by Avantra. Together with the I(unified_sap_sid) parameter it identifies a
          SAP system.
        required: true
        type: str
    exists_state:
        description:
        - If C(present) the SAP system with the given parameter is created in case is does
          not exist or modified in case it exists.
        - If C(absent) the SAP system identified by the I(unified_sap_sid) and I(customer_name)
          is deleted if it exists.
        required: false
        default: present
        type: str
        choices:
            - present
            - absent
    real_sap_sid:
        description:
        - The B(Real SAP SID) of the SAP system. Maximum allowed length is 3 characters.
        - If C(exists_state=present) and the SAP system has to be created this parameter is mandatory.
        required: false
        type: str
    description:
        description: The description for the SAP system.
        required: false
        type: str
    notes:
        description: The notes for the SAP system.
        required: false
        type: str
    application_type:
        description: The application type (one of the defined in the customizations).
        required: false
        type: str
    database:
        description: Configures the database detail for the SAP system.
        required: false
        type: dict
        suboptions:
            monitoring_server_system_id:
                description:
                - The system ID of the server monitoring the database.
                type: str
                required: false
            host:
                description:
                - Defines the database host.
                type: str
                required: false
            port:
                description:
                - Defines the database port.
                type: str
                required: false
            name:
                description:
                - Configures the database name.
                type: str
                required: false

    credentials:
        description:
        - Add credentials to this SAP system. See the examples for more information on how
          to set the different credential types. The key for the child objects is one of the credential
          keys found in Avantra.
        - We highly recommend to use Ansible Vaults to protect you sensitive content.
        type: dict
        required: false

    remote_monitoring_entry_point:
        description: Configures the remote entrypoint for agentless SAP system.
        type: str
        required: false

    remote_monitoring_server_system_id:
        description: Configures the server monitoring the remote SAP system.
        type: str
        required: false

    run_state:
        description:
        - If C(started) and the current state is C(run_state=stopped) or C(run_state=unknown) the SAP system will
          be started.
        - If C(stopped) and the current state is C(run_state=started) or C(run_state=unknown) the SAP system will
          be started.
        - If C(restarted) the SAP system will be restarted.
        - B(Note:) if C(exists_state=absent) and the SAP system exists the run state change will be applied before
          the SAP system is deleted. If C(exists_state=present) the run state change will be executed after the SAP
          system has been created.
        type: str
        choices:
            - started
            - stopped
            - restarted
    run_options:
        description:
        - Allows you to configure the behaviour of the run_state changes.
        type: dict
        required: false
        suboptions:
            always_execute:
                description:
                - Ignore the current state and just execute the start/stop/restart.
                required: false
                type: bool
                default: false
            monitoring:
                description:
                - If C(run_state=started) this parameter defaults to true.
                - If C(run_state=stopped) this parameter defaults to false.
                - If C(run_state=restarted) this parameter is ignored.
                type: bool
            with_database:
                description: Starts/Stops/Restarts the SAP System including the database.
                required: false
                type: bool
                default: false
            with_servers:
                description:
                - Starts/Stops/Restarts all cloud servers, the SAP database (full) and the SAP System.
                - If C(with_servers=true) then C(with_database=true) is needed as well
                  and C(with_system_db_if_hana) must not be true.
                required: false
                type: bool
                default: false
            with_system_db_if_hana:
                description:
                - Starts/Stops/Restarts the SAP HANA System DB, all HANA tenants and the SAP System.
                - If C(with_system_db_if_hana=true) then C(with_database=true) is needed as well
                  and C(with_server) must not be true.
                required: false
                type: bool
                default: false
            check_db_state:
                description:
                - If C(with_database=true) then the task checks the database state before starting SAP system
                  (only for Linux, uses R3Trans).
                type: bool
                required: false
                default: true
            wait_seconds:
                description:
                - Defines the wait time in seconds after a server start before executing next steps.
                required: false
                default: 60
                type: int
            restart_wait_seconds:
                description:
                - Defines the wait time in seconds after a stop before start process is started.
                required: false
                default: 5
                type: int
            soft_timeout:
                description:
                - Defines the soft timeout a timeout in seconds for a soft shutdown via SIGQUIT, if the timeout expires
                  a hard shutdown is used. After the soft timeout, logged in users are automatically logged out.
                required: false
                default: 0
                type: int
            force_stop:
                description:
                - Avantra checks for known running applications (ie. applications with monitoring turned on) and cancels
                  a stop if some are found. With C(force_stop=true), the server will be stopped in any case.
                required: false
                default: true
                type: bool
            send_user_info:
                description:
                - Send a message to all users logged in with SAPGUI. Use this option together with C(soft_timeout)
                  setting.
                required: false
                default: false
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
    - avantra.core.option_custom_attributes
    - avantra.core.option_monitoring
    - avantra.core.option_timezone
    - avantra.core.option_system_role
    - avantra.core.version_added_23_0
    - avantra.core.notes_ansiblevaults
    - avantra.core.option_application_type
"""

EXAMPLES = r"""
- name: Delete SAP system from Avantra if it exists
  avantra.core.sapsystem:
    exists_state: absent
    unified_sap_sid: "UNF_SAP_SYS"
    customer_name: "mis"

- name: Create SAP system if it doesn't exist
  avantra.core.sapsystem:
    exists_state: present
    unified_sap_sid: "AVA_EXA"
    real_sap_sid: "EXA"
    customer_name: "Example Customer"
    system_role: "Development"
    timezone: "UTC"
    monitoring: true
    notes: "Some notes"
    description: "A description"
    database:
      monitoring_server_system_id: 253
      host: "golf"
      name: "EXA"
      port: 12345
    credentials:
      # SAP control user
      avantra.sapControl:
        cred_type: sap_control
        username: <user>
        password: <password>
      # ABAP user
      avantra.defaultRfcUser:
        cred_type: rfc
        username: <user>
        password: <password>
        client: 000
      # ABAP database user
      avantra.abapDbSchema:
        cred_type: basic
        username: <user>
        password: <password>
      # J2EE user
      avantra.j2eeUser:
        cred_type: basic
        username: <user>
        password: <password>
      # J2EE database user
      avantra.javaDbSchema:
        cred_type: basic
        username: <user>
        password: <password>

- name: Restart the SAP system
  avantra.core.sapsystem:
    exists_state: present
    run_state: restarted
    run_options:
      execution_name: "Restart the AVA_EXE SAP system"
    unified_sap_sid: "AVA_EXA"
    customer_name: Avantra

- name: Restart the SAP system with its database and servers
  avantra.core.sapsystem:
    exists_state: present
    run_state: restarted
    run_options:
      execution_name: "Restart the AVA_EXE SAP system with its database and servers"
      with_database: true
      with_servers: true
    unified_sap_sid: "AVA_EXA"
    customer_name: Avantra
"""

RETURN = r"""
sap_system:
    description:
    - If C(exists_state=present) and the SAP system can be identified the system information is returned.
    type: dict
    returned: present
"""

from datetime import datetime, timedelta

from ansible_collections.avantra.core.plugins.module_utils.avantra.utils import (
    parse_api_date_time
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.system_actions import (
    SAP_SYSTEM_START,
    SAP_SYSTEM_STOP,
    SAP_SYSTEM_RESTART,
    SAP_SYSTEM_WITH_DB_START,
    SAP_SYSTEM_WITH_DB_STOP,
    SAP_SYSTEM_WITH_DB_RESTART,
    SAP_SYSTEM_WITH_DB_AND_HANA_START,
    SAP_SYSTEM_WITH_DB_AND_HANA_STOP,
    SAP_SYSTEM_WITH_DB_AND_HANA_RESTART,
    SAP_SYSTEM_WITH_DB_AND_SERVER_START,
    SAP_SYSTEM_WITH_DB_AND_SERVER_STOP,
    SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.api import (
    create_argument_spec,
    AVANTRA_TOKEN,
    AVANTRA_API_USER,
    AVANTRA_API_PASSWORD,
    AvantraAnsibleModule
)

from ansible_collections.avantra.core.plugins.module_utils.avantra.sapsystem import (
    create_sapsystem,
    update_sapsystem,
    delete_sapsystem,
    fetch_sapsystem,
    turn_monitoring_on,
    turn_monitoring_off
)


def _check_run_state_arguments(module, with_database, with_servers, with_system_db_if_hana):
    if with_servers and with_system_db_if_hana:
        module.fail_json(msg="Unsupported flag combination: only one of ['with_servers', 'with_system_db_if_hana'] "
                             "can be set to true")
    elif with_servers and not with_database:
        module.fail_json(msg="Unsupported flag combination: 'with_database' has to be set to true in case "
                             "'with_servers' is set to true")
    elif with_system_db_if_hana and not with_database:
        module.fail_json(msg="Unsupported flag combination: 'with_database' has to be set to true in case "
                             "'with_system_db_if_hana' is set to true")


def _get_run_state(sap_system):
    if sap_system is not None:
        # At the moment there is no way to tell what is the correct run_state of a SAP system. Here
        # we check whether there is a SystemAlive check not older than 10 minutes.
        checks = sap_system.pop("checks", None)
        if len(checks) > 0 and hasattr(checks[0], "last_refresh"):
            last_refresh = parse_api_date_time(checks[0]["last_refresh"])
            if last_refresh > datetime.now() - timedelta(minutes=10) and checks[0]["last_refresh"] == "OK":
                return "started"

    return "unknown"


def ensure_started(module, sap_system, result):
    prev_run_state = _get_run_state(sap_system)
    result["diff"]["before"]["run_state"] = prev_run_state

    run_options = module.params.get("run_options")
    with_database = run_options["with_database"]
    with_servers = run_options["with_servers"]
    with_system_db_if_hana = run_options["with_system_db_if_hana"]

    _check_run_state_arguments(module, with_database, with_servers, with_system_db_if_hana)

    if not with_database:
        action = SAP_SYSTEM_START
    elif with_servers:
        action = SAP_SYSTEM_WITH_DB_AND_SERVER_START
    elif with_system_db_if_hana:
        action = SAP_SYSTEM_WITH_DB_AND_HANA_START
    else:
        action = SAP_SYSTEM_WITH_DB_START

    if prev_run_state != "started" or run_options.get("always_execute"):
        result["action_result"] = module.execute_system_action(
            action,
            system_id=sap_system["id"],
            execution_name=run_options["execution_name"],
            args={
                "SET_MONI_ON": run_options.get("monitoring", True),
                "WAIT_SECONDS": run_options.get("wait_seconds"),
                "CHECK_DB_STATE": run_options.get("check_db_state")
            }
        )
        result["diff"]["after"]["run_state"] = "started"
        result["changed"] = True


def ensure_stopped(module, sap_system, result):
    prev_run_state = _get_run_state(sap_system)
    result["diff"]["before"]["run_state"] = prev_run_state

    run_options = module.params.get("run_options")

    with_database = run_options["with_database"]
    with_servers = run_options["with_servers"]
    with_system_db_if_hana = run_options["with_system_db_if_hana"]

    _check_run_state_arguments(module, with_database, with_servers, with_system_db_if_hana)

    if not with_database:
        action = SAP_SYSTEM_STOP
    elif with_servers:
        action = SAP_SYSTEM_WITH_DB_AND_SERVER_STOP
    elif with_system_db_if_hana:
        action = SAP_SYSTEM_WITH_DB_AND_HANA_STOP
    else:
        action = SAP_SYSTEM_WITH_DB_STOP

    if prev_run_state != "stopped" or run_options.get("always_execute"):
        result["action_result"] = module.execute_system_action(
            action,
            system_id=sap_system["id"],
            execution_name=run_options["execution_name"],
            args={
                "SET_MONI_OFF": run_options.get("monitoring", False),
                "FORCE_STOP": run_options["force_stop"],
                "SEND_USER_INFO": run_options["send_user_info"],
                "SOFTTIMEOUT": run_options["soft_timeout"]
            }
        )
        result["diff"]["after"]["run_state"] = "stopped"
        result["changed"] = True


def ensure_restarted(module, sap_system, result):
    prev_run_state = _get_run_state(sap_system)
    result["diff"]["before"]["run_state"] = prev_run_state

    run_options = module.params.get("run_options")
    with_database = run_options["with_database"]
    with_servers = run_options["with_servers"]
    with_system_db_if_hana = run_options["with_system_db_if_hana"]

    _check_run_state_arguments(module, with_database, with_servers, with_system_db_if_hana)

    if not with_database:
        action = SAP_SYSTEM_RESTART
    elif with_servers:
        action = SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART
    elif with_system_db_if_hana:
        action = SAP_SYSTEM_WITH_DB_AND_HANA_RESTART
    else:
        action = SAP_SYSTEM_WITH_DB_RESTART

    result["action_result"] = module.execute_system_action(
        action,
        system_id=sap_system["id"],
        execution_name=run_options["execution_name"],
        args={
            "SOFTTIMEOUT": run_options["soft_timeout"],
            "SEND_USER_INFO": run_options["send_user_info"],
            # This can be removed in case servers are not involved...
            "FORCE_STOP": run_options["force_stop"],
            "CHECK_DB_STATE": run_options["check_db_state"],
            "RESTART_WAIT_SECONDS": run_options["restart_wait_seconds"]
        }
    )
    result["diff"]["after"]["run_state"] = "restarted"
    result["changed"] = True


def ensure_sapsystem_monitoring(module, sap_system, result):
    if sap_system["monitor_off"] == "true":
        prev_monitoring = True
    else:
        prev_monitoring = False

    monitoring = module.params.get("monitoring")

    if monitoring is not None and prev_monitoring != monitoring:
        if monitoring:
            success, msg, sap_system_after = turn_monitoring_on(module, sap_system["id"])
        else:
            success, msg, sap_system_after = turn_monitoring_off(module, sap_system["id"])

        if success:
            sap_system = sap_system_after

    return sap_system


def ensure_sapsystem_present(module, customer_name, unified_sap_sid):
    result = {
        "changed": False
    }

    success, msg, sap_system = fetch_sapsystem(module,
                                               unified_sap_sid=unified_sap_sid,
                                               customer_name=customer_name)

    if sap_system is None:
        prev_exists_state = "absent"
    else:
        prev_exists_state = "present"

    diff = {
        "before": {"exists_state": prev_exists_state},
        "after": {"exists_state": "present"}
    }

    diff["before"]["sap_system"] = None
    if prev_exists_state == "absent":
        # Create the SAP system -> nees real sap sid and system role.

        if module.params.get("system_role") is None:
            module.fail_json(msg="system_role argument is missing", result=result)
        elif module.params.get("real_sap_sid") is None:
            module.fail_json(msg="real_sap_sid argument is missing", result=result)

        success, msg, sap_system = create_sapsystem(module, customer_name=customer_name,
                                                    unified_sap_sid=unified_sap_sid)
        if success:
            diff["after"]["sap_system"] = sap_system

            result.update(
                changed=True,
                sap_system=sap_system
            )
        else:
            module.fail_json(msg=msg, result=result)

    else:
        success, msg, sap_system = update_sapsystem(module, sap_system_id=sap_system.get("id"))
        if success:
            diff["after"]["sap_system"] = sap_system
            result.update(
                changed=True,
                sap_system=sap_system
            )
        else:
            module.fail_json(msg=msg, result=result)

    result["diff"] = diff

    sap_system = ensure_sapsystem_monitoring(module, sap_system, result)

    run_state = module.params.get("run_state")
    if run_state == "started":
        ensure_started(module, sap_system, result)
    elif run_state == "stopped":
        ensure_stopped(module, sap_system, result)
    elif run_state == "restarted":
        ensure_restarted(module, sap_system, result)
    else:
        pass

    result["sap_system"] = sap_system

    return result


def ensure_sapsystem_absent(module, customer_name, unified_sap_sid):
    result = {
        "changed": False
    }

    success, msg, sap_system = fetch_sapsystem(module,
                                               unified_sap_sid=unified_sap_sid,
                                               customer_name=customer_name)

    if sap_system is None:
        prev_exists_state = "absent"
    else:
        prev_exists_state = "present"

    diff = {
        "before": {
            "exists_state": prev_exists_state,
            "sap_system": sap_system
        },
        "after": {
            "exists_state": "absent",
            "sap_system": None
        }
    }
    result["diff"] = diff

    if prev_exists_state == "present":

        run_state = module.params.get("run_state")
        if run_state == "started":
            ensure_started(module, sap_system, result)
        elif run_state == "stopped":
            ensure_stopped(module, sap_system, result)
        elif run_state == "restarted":
            ensure_restarted(module, sap_system, result)
        else:
            pass

        # Delete the SAP system
        success, msg = delete_sapsystem(module, sap_system["id"])
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

        "run_state": dict(type='str', choices=["started", "stopped", "restarted"]),
        "run_options": dict(type='dict', default={},
                            options=dict(
                                always_execute=dict(type="bool", default=False),
                                monitoring=dict(type="bool"),
                                with_database=dict(type='bool', default=False),
                                with_servers=dict(type='bool', default=False),
                                with_system_db_if_hana=dict(type='bool', default=False),
                                check_db_state=dict(type='bool', default=True),
                                wait_seconds=dict(type='int', default=60),
                                soft_timeout=dict(type='int', default=0),
                                restart_wait_seconds=dict(type='int', default=5),
                                force_stop=dict(type='bool', default=True),
                                send_user_info=dict(type='bool', default=False),
                                execution_name=dict(type='str'))),
        "unified_sap_sid": dict(type='str', required=True),
        "customer_name": dict(type='str', required=True),
        "real_sap_sid": dict(type='str'),
        "credentials": dict(type='dict'),
        "description": dict(type='str'),
        "monitoring": dict(type='bool'),
        "application_type": dict(type='str'),
        "system_role": dict(type='str'),
        "timezone": dict(type='str'),
        "notes": dict(type='str'),
        "custom_attributes": dict(type='dict', default={}),
        "remote_monitoring_entry_point": dict(type='str'),
        "remote_monitoring_server_system_id": dict(type='str'),
        "database": dict(type="dict",
                         options=dict(
                             monitoring_server_system_id=dict(type="str", ),
                             host=dict(type="str", ),
                             port=dict(type="str", ),
                             name=dict(type="str", )
                         )),
    })

    module = AvantraAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[
            (AVANTRA_API_USER, AVANTRA_API_PASSWORD),
            ("unified_sap_sid", "customer_name")
        ],
        required_one_of=[
            (AVANTRA_API_USER, AVANTRA_TOKEN)
        ]
    )

    # TODO:
    if module.check_mode:
        module.exit_json(**result)

    # Fetch the SAP system
    unified_sap_sid = module.params.get("unified_sap_sid")
    customer_name = module.params.get("customer_name")

    exists_state = module.params.get("exists_state").lower()
    if exists_state == "present":
        result = ensure_sapsystem_present(module, customer_name, unified_sap_sid)
    elif exists_state == "absent":
        result = ensure_sapsystem_absent(module, customer_name, unified_sap_sid)
    else:
        module.fail_json(msg="Wrong exists_state: {0}".format(exists_state))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
