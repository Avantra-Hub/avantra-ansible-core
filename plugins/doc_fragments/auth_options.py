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


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    avantra_api_url:
        description:
        - A valid URL pointing to an Avantra UI.
        - For example C(https://avantra-ui/xn)
        required: true
        type: str
    avantra_api_user:
        description:
        - Valid Avantra user principal.
        required: true
        type: str
    avantra_api_password:
        description:
        - The password or API key for the selected Avantra user.
        - We highly recommend to use Ansible Vaults to protect you sensitive content.
        required: true
        type: str
    validate_certs:
        description:
        - If C(false), SSL certificate verification is disabled.
        - Use this when connecting to Avantra instances with self-signed certificates.
        required: false
        type: bool
        default: true
"""
    TOKEN = r"""
options:
    avantra_api_url:
        description:
        - A valid URL pointing to an Avantra UI.
        - For example C(https://avantra-ui/xn)
        required: true
        type: str
    avantra_api_user:
        description:
        - Valid Avantra user principal.
        required: false
        type: str
    avantra_api_password:
        description:
        - The password or API key for the selected Avantra user.
        - We highly recommend to use Ansible Vaults to protect you sensitive content.
        required: false
        type: str
    token:
        description: >
            The token used to authenticate during the task execution. A token can be
            fetched with the M(avantra.core.login) module. If I(token) is
            defined I(avantra_api_user) and I(avantra_api_password) are not necessary.
        required: false
        type: str
    validate_certs:
        description:
        - If C(false), SSL certificate verification is disabled.
        - Use this when connecting to Avantra instances with self-signed certificates.
        required: false
        type: bool
        default: true
"""
