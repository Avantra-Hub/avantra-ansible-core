#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.avantra.core.plugins.action._avantra_base import AvantraActionModule

class ActionModule(AvantraActionModule):
    def run(self, tmp=None, task_vars=None):
        return super(ActionModule, self).run(tmp, task_vars)
