#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError, AnsibleActionFail
from datetime import datetime
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        with open('/tmp/avantra-ansible-module.log', 'a', encoding="utf-8") as f:
            f.write(f"Action-Plugin: run(...) {datetime.now()}\n")

            super(ActionModule, self).run(tmp, task_vars)

            module_args = self._task.args.copy()
            f.write(f"Action-Plugin: module_name={self._task.action}\n")
            f.write(f"Action-Plugin: module_args={module_args}\n")
            f.write(f"Action-Plugin: task_vars={task_vars}\n")
            f.flush()

            try:
                avantra_api_user = task_vars['avantra_api_user']
                avantra_api_password = task_vars['avantra_api_password']
                avantra_api_url = task_vars['avantra_api_url']
            except KeyError as e:
                raise AnsibleActionFail(f"Undefined variable '{e.args[0]}'")

            module_args['avantra_api_user'] = avantra_api_user
            module_args['avantra_api_password'] = avantra_api_password
            module_args['avantra_api_url'] = avantra_api_url

            module_return = self._execute_module(module_args=module_args, task_vars=task_vars)
            if module_return.get("warnings") is not None:
                for w in module_return["warnings"]:
                    display.warning(w)

            ret = dict()
            if not module_return.get('failed'):
                for key, value in module_return.items():
                    if key in ['message', 'original_message', 'changed', 'ansible_facts']:
                        display.display(f"{key} => {value}")
                        ret[key] = value

            return dict(ret)
