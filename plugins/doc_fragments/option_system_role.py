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
     system_role:
        description:
        - Configures the system role.
        - If C(exists_state=present) and the system has to be created this parameter is mandatory.
        - "By default the following roles are available: C(Consolidation), C(Development), C(Education),
          C(Integration), C(Production), C(Quality assurance), C(Sandpit), C(Test). The can be customized
          in Avantra."
        required: false
        type: str
"""
