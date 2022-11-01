# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
    avantra_api_url:
        description: This is a valid pointing to a Avantra UI.
        required: true
        type: str
    avantra_api_user:
        description: A valid Avantra user name.            
        required: true
        type: str
    avantra_api_password:
        description: The password or API key for the selected Avantra user.            
        required: true
        type: str
"""
    TOKEN = r"""
options:
    avantra_api_url:
        description: This is a valid pointing to a Avantra UI.
        required: true
        type: str
    avantra_api_user:
        description: A valid Avantra user name.            
        required: false
        type: str
    avantra_api_password:
        description: The password or API key for the selected Avantra user.            
        required: false
        type: str
    avantra_token:
        description: >
            The token used to authenticate during task execution. An token can be
            fetched with the M(avantra.core.login) module. If I(avantra_token) is 
            defined I(avantra_api_user) and I(avantra_api_password) are not necessary.         
        required: false
        type: str
"""

