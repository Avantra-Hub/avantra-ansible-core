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

from typing import Dict
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError, AnsibleActionFail
from datetime import datetime
from ansible.utils.display import Display

display = Display()


def _load_key(module_args: Dict, task_vars: Dict, key: str):
    if key not in module_args and key in task_vars:
        module_args[key] = task_vars[key]


class AvantraActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        display.vv("{0} |avantra.core |ACTION | run".format(datetime.now()))
        super(AvantraActionModule, self).run(tmp, task_vars)

        module_args = self._task.args.copy()
        display.vv("{0} |avantra.core |ACTION |module_name={1}".format(datetime.now(), self._task.action))
        display.vv("{0} |avantra.core |ACTION |module_args={1}".format(datetime.now(), module_args))
        display.vv("{0} |avantra.core |ACTION |task_vars={1}".format(datetime.now(), task_vars))

        # We have to check for those variables if the task does not define it.
        if "avantra_token" not in module_args:
            for p in ["avantra_api_user", "avantra_api_password", "avantra_api_url"]:
                _load_key(module_args, task_vars, p)
                if p not in module_args:
                    raise AnsibleActionFail(f"Couldn't find value for parameter: '{p}'")
        else:
            for p in ["avantra_api_url"]:
                _load_key(module_args, task_vars, p)
                if p not in module_args:
                    raise AnsibleActionFail("Couldn't find value for parameter: '{0}'".format(p))

        display.vv("{0} |avantra.core |ACTION |execute_module: invoke".format(datetime.now()))
        module_return = self._execute_module(module_args=module_args, task_vars=task_vars)
        if module_return.get("warnings") is not None:
            for w in module_return["warnings"]:
                display.warning(w)

        display.vv("{0} |avantra.core |ACTION |execute_module: module_return={1}".format(datetime.now(), module_return))

        return dict(module_return)
