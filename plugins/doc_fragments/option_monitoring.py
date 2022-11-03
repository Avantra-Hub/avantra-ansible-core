# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
    monitoring:
        description: 
        - Should the monitoring be turned on or off. 
        - This applies only to C(exists_state=present).
        - For C(exists_state=absent) this parameter will be ignored.
        required: false
        type: bool
"""
