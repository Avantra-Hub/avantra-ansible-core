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

        display.v(f"{datetime.now()} |avantra.core |ACTION | run")
        super(AvantraActionModule, self).run(tmp, task_vars)

        module_args = self._task.args.copy()
        display.v(f"{datetime.now()} |avantra.core.customer |ACTION |module_name={self._task.action}")
        display.v(f"{datetime.now()} |avantra.core.customer |ACTION |module_args={module_args}")
        display.v(f"{datetime.now()} |avantra.core.customer |ACTION |task_vars={task_vars}")

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
                    raise AnsibleActionFail(f"Couldn't find value for parameter: '{p}'")

        display.v(f"{datetime.now()} |avantra.core |ACTION |execute_module: invoke")
        module_return = self._execute_module(module_args=module_args, task_vars=task_vars)
        if module_return.get("warnings") is not None:
            for w in module_return["warnings"]:
                display.warning(w)

        display.v(f"{datetime.now()} |avantra.core |ACTION |execute_module: module_return={module_return}")

        return dict(module_return)
