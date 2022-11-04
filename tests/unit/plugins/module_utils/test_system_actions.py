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

from ansible_collections.avantra.core.plugins.module_utils.avantra.system_actions import (
    SERVER_START,
    SERVER_STOP,
    SAP_SYSTEM_START,
    SAP_SYSTEM_STOP,
    SAP_SYSTEM_RESTART,
    SAP_SYSTEM_WITH_DB_START,
    SAP_SYSTEM_WITH_DB_STOP,
    SAP_SYSTEM_WITH_DB_RESTART,
    SAP_SYSTEM_WITH_DB_AND_HANA_START,
    SAP_SYSTEM_WITH_DB_AND_HANA_STOP,
    SAP_SYSTEM_WITH_DB_AND_HANA_RESTART,
    SAP_SYSTEM_WITH_DB_AND_SERVER_START,
    SAP_SYSTEM_WITH_DB_AND_SERVER_STOP,
    SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART
)


def test_values():
    assert SERVER_START == 20
    assert SERVER_STOP == 21
    assert SAP_SYSTEM_START == 1
    assert SAP_SYSTEM_STOP == 2
    assert SAP_SYSTEM_RESTART == 201
    assert SAP_SYSTEM_WITH_DB_START == 32
    assert SAP_SYSTEM_WITH_DB_STOP == 33
    assert SAP_SYSTEM_WITH_DB_RESTART == 202
    assert SAP_SYSTEM_WITH_DB_AND_HANA_START == 34
    assert SAP_SYSTEM_WITH_DB_AND_HANA_STOP == 35
    assert SAP_SYSTEM_WITH_DB_AND_HANA_RESTART == 203
    assert SAP_SYSTEM_WITH_DB_AND_SERVER_START == 36
    assert SAP_SYSTEM_WITH_DB_AND_SERVER_STOP == 37
    assert SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART == 204
