# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
     system_role:
        description: 
        - Configures the system role.
        - If C(exists_state=present) and the system has to be created this parameter is mandatory.
        choices:        
            - Consolidation
            - Development
            - Education
            - Integration
            - Production
            - Quality assurance
            - Sandpit
            - Test
            - ... customized roles
                    
        required: false
        type: str  
"""
