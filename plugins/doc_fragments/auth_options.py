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

